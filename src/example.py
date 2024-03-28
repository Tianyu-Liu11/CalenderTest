import json
import logging
import re

from ninja_code_run_client.base_client import PauseExecutionError
from ninja_code_run_client.models import RunOutput
from ninja_code_run_client.websocket_async_client import NinjaCodeRunAsync
from ninja_common.context import context
from ninja_common.metrics import NinjaMetricsCollector
from ninja_common.models.callback_models import ActionStatus, AgentUpdate
from ninja_guidance import guidance

from ninja_calendar_agent_shared.models import LLMConfig, LLMModel
from ninja_calendar_agent_worker.agent.nudge_utils import nudge
from ninja_calendar_agent_worker.agent.planner_program import PLANNER_CONSTITUTION
from ninja_calendar_agent_worker.agent.shared import tools
from ninja_calendar_agent_worker.agent.utils import get_user_details_prompt_message
from ninja_calendar_agent_worker.context import (
    get_agent_progress,
    is_in_debug_response_mode,
    is_valid_nudge_mode,
)
from ninja_calendar_agent_worker.exceptions import (
    CodeRunTimeoutException,
    ContactAgentUncertaintyException,
    HandledTaskHaltingException,
    NoMoreChainStepsException,
    PauseAgentForUserInputException,
    TaskIsOffloadedException,
)
from ninja_calendar_agent_worker.llm.factory import LLMFactory
from ninja_calendar_agent_worker.models.agent_models import Agent, SummarizerCodeRunData
from ninja_calendar_agent_worker.models.common_models import CodeExecStep
from ninja_calendar_agent_worker.models.snapshot_models import (
    CODE_EXEC_STEPS_DATE_FILE_NAME,
    CodeExecStepsData,
    GuidanceProgramS3SnapshotData,
)
from ninja_calendar_agent_worker.session import tasks_api_client
from ninja_calendar_agent_worker.utils import (
    callback_client,
    mark_task_as_stopped,
    prefix_debug_message_with_agent_progress,
    snapshotter,
    task_is_stopping,
)

_MAX_CODE_EXECUTOR_CHAIN_STEPS = 15
_MAX_CODE_EXECUTOR_OUTPUT_LINES = 50
_SCHEDULER_TOOL_USED = "create_meeting_between_multiple_people("
_PREFIX_FOR_CONTACTS_AGENT_UNCERTAINTY = "ValueError: ContactAgentUncertaintyException: "
_MAX_FALLBACK_COUNT = 3


CODE_EXECUTOR_CONSTITUTION = PLANNER_CONSTITUTION

CODE_EXECUTOR_PROMPT = """
{{#system~}}
{{llm.default_system_prompt}}
{{~/system}}

{{#user~}}
{{constitution}}

#####\nBegin!\nTask: {{task}}
{{~/user}}

{{#assistant~}}
{{plan}}
{{~/assistant~}}

{{#user~}}
Continue
{{~/user}}

{{#each previous_rounds}}
{{#assistant~}} {{this.input}} {{/assistant~}}
{{#user~}} {{this.output}} {{~/user}}
{{~/each}}

{{#geneach 'commands'}}
{{#assistant~}}
{{gen 'this.command' max_new_tokens=512}}
{{~/assistant~}}
{{#user~}}
{{await 'output'}}
{{~/user}}
{{/geneach}}
"""


code_executor_program = guidance(CODE_EXECUTOR_PROMPT)


def scheduler_tool_was_successfully_used(run_output_str: str, run_error_str: str) -> bool:
    if run_error_str:
        return False

    error_text_list = ["Error:", "You MUST"]
    return not any(error_text in run_output_str for error_text in error_text_list)


def should_fallback_to_other_model(
    request_llm_config: LLMConfig, fallback_llm_config: LLMConfig, fallback_count: int
) -> bool:
    return (
        not request_llm_config.model == fallback_llm_config.model
        and fallback_count < _MAX_FALLBACK_COUNT
    )


async def run_code_executor_program(
    python_repl: NinjaCodeRunAsync,
    agent: Agent,
    metrics: NinjaMetricsCollector,
    logger: logging.Logger,
) -> list[SummarizerCodeRunData]:
    fallback_count = 0
    agent_progress = get_agent_progress()

    try:
        is_pausing_for_user_input = False
        resuming_from_user_input = agent.resume_from_user_input_code_exec_round is not None

        code_exec_steps_left = _MAX_CODE_EXECUTOR_CHAIN_STEPS - len(agent.code_exec_rounds)
        current_code_exec_round: CodeExecStep | None = None

        # Define fallback & current models
        fallback_model = LLMModel.GPT_4_1106_PREVIEW
        fallback_llm_config = agent.llm_config.copy(
            update={"model": fallback_model, "model_url": None}
        )
        current_model = agent.llm_config.model

        executing_program = None
        llm_model = agent.llm_config.model

        logger.info(f"Code executor using model: {llm_model}")
        logger.info(f"Code executor using model_url: {agent.llm_config.model_url}")

        few_shots = []

        if not resuming_from_user_input:
            executing_program = await _get_new_code_exec_program(
                agent=agent,
                llm_config_to_use=agent.llm_config,
                few_shots=few_shots,
            )

        prev_llm_reply_with_code = None

        for step in range(code_exec_steps_left):
            should_consider_fallback = False
            scheduler_tool_used_in_this_step = False

            if not resuming_from_user_input:
                await agent_progress.start_current_action()
                llm_reply_with_code = executing_program["commands"][-1]["command"] + "\n"
                if is_valid_nudge_mode():
                    llm_reply_with_code = await nudge(llm_reply_with_code, f"Edit Step {step + 1}")
            else:
                llm_reply_with_code = agent.resume_from_user_input_code_exec_round.input
                resuming_from_user_input = False

            _python_code_re_pattern = "```python\n(.*?)```"
            llm_reply_without_code = re.sub(
                _python_code_re_pattern, "", llm_reply_with_code, flags=re.DOTALL
            )
            python_code_list = re.findall(_python_code_re_pattern, llm_reply_with_code, re.DOTALL)

            if _SCHEDULER_TOOL_USED in llm_reply_with_code:
                scheduler_tool_used_in_this_step = True

            if context.test_session_id:
                logger.info("llm_reply_with_code: \n%s", llm_reply_with_code)

            if prev_llm_reply_with_code == llm_reply_with_code:
                logger.info("Agent detected repeating itself")
                # Let's tell it off for repeating itself!
                total_code_output = "You keep repeating yourself - lets design a different idea - probably lets simplify it"
                should_consider_fallback = True
            else:
                # Detect agent completion
                if not python_code_list:
                    logger.info("Agent completion detected due to lack of python code in reply")
                    break

                total_code_output = ""
                for code_block in python_code_list:
                    code_block = code_block.replace(
                        "*TEXT_TIMEZONE*",
                        agent.user_details.time_zone,
                    )
                    code_block = code_block.replace("*DEFAULT_DURATION*", "get_default_duration()")

                    current_code_exec_round = CodeExecStep(input=llm_reply_with_code)

                    # CHECK IF TASK HALTING BEFORE WE RUN CODE
                    if await task_is_stopping(context.task_id, tasks_api_client):
                        await mark_task_as_stopped(
                            callback_url=agent.callback_url,
                            client=callback_client,
                            logger=logger,
                            metrics=metrics,
                        )
                        raise HandledTaskHaltingException()

                    run_output = await python_repl.run(code_block)
                    run_output_str = run_output.error_str or run_output.content_str

                    if not run_output.error_str:
                        # Assume success if no error returned from REPL
                        await agent_progress.complete_current_action(ActionStatus.COMPLETED)
                    else:
                        should_consider_fallback = True

                    # Handle empty output
                    if run_output_str == "":
                        run_output_str = "Ok, done"

                    # Handle long output by truncating it
                    if run_output_str.count("\n") > _MAX_CODE_EXECUTOR_OUTPUT_LINES:
                        # Split the string into lines
                        lines = run_output_str.splitlines()

                        # Get the first 50 lines
                        first_50_lines = lines[:50]

                        # Join them back into a string
                        first_50_lines_str = "\n".join(first_50_lines)

                        run_output_str = (
                            "after I run the command the output length looks very long - here is the first 50 line\n"
                            + first_50_lines_str
                        )

                    current_code_exec_round.output = run_output_str

                    if is_in_debug_response_mode():
                        debug_message = f"LLM CODE INPUT & THOUGHTS ({current_model}):\n {llm_reply_with_code}\n"
                        debug_message += f"CODE OUTPUT:\n {run_output_str}"
                        logger.debug(debug_message)
                        await agent_progress.do_callback(
                            agent_update=AgentUpdate(
                                message=prefix_debug_message_with_agent_progress(debug_message),
                                conversation_id=context.conversation_id,
                                task_id=context.task_id,
                            ),
                        )

                    # We detect that scheduler tool was successfully used and stop the agent
                    # from doing anything else. Eventually we want to remove this behavior and
                    # allow agent to call scheduler, suspend itself, and then continue
                    # when scheduler is done or needs the agent.
                    #
                    # TODO: Move detection to control plane
                    if scheduler_tool_used_in_this_step and scheduler_tool_was_successfully_used(
                        run_output_str, run_output.error_str
                    ):
                        logger.info("Agent detected scheduler tool used - stopping agent")
                        raise TaskIsOffloadedException()

                    total_code_output += run_output_str

                    # Check Contact Agent Uncertainty
                    _contact_agent_uncertainty_check(run_output)

                    # Terminate agent if code run times out
                    _code_run_timeout_check(run_output_str)

            prev_llm_reply_with_code = llm_reply_with_code
            agent.summarizer_code_run_data.append(
                SummarizerCodeRunData(
                    llm_reply_without_code=llm_reply_without_code,
                    executed_code_output="\n" + total_code_output,
                )
            )
            agent.code_exec_rounds.append(current_code_exec_round)

            if (
                agent.llm_config.allow_fallback
                and should_consider_fallback
                and should_fallback_to_other_model(
                    agent.llm_config, fallback_llm_config, fallback_count
                )
            ):
                if current_model == fallback_llm_config.model:
                    executing_program = await executing_program(output="\n" + total_code_output)
                    logger.info(f"Continuing to use fallback model: {fallback_llm_config.model}")
                else:
                    logger.info(f"Falling back to model: {fallback_llm_config.model}")
                    current_model = fallback_llm_config.model
                    executing_program = await _get_new_code_exec_program(
                        agent=agent,
                        llm_config_to_use=fallback_llm_config,
                        few_shots=few_shots,
                    )

                fallback_count += 1
            else:
                if current_model == agent.llm_config.model:
                    logger.info(f"Continuing to use model: {agent.llm_config.model}")
                    if agent.resume_from_user_input_code_exec_round:
                        executing_program = await _get_new_code_exec_program(
                            agent=agent,
                            llm_config_to_use=agent.llm_config,
                            few_shots=few_shots,
                        )
                    else:
                        executing_program = await executing_program(output="\n" + total_code_output)
                else:
                    logger.info(f"Switching back to model: {agent.llm_config.model}")
                    current_model = agent.llm_config.model
                    executing_program = await _get_new_code_exec_program(
                        agent=agent,
                        llm_config_to_use=agent.llm_config,
                        few_shots=few_shots,
                    )

            # Reach max chain steps and not finished
            if step == _MAX_CODE_EXECUTOR_CHAIN_STEPS - 1:
                raise NoMoreChainStepsException()

    except PauseExecutionError:
        agent.resume_from_user_input_code_exec_round = current_code_exec_round
        is_pausing_for_user_input = True
        raise PauseAgentForUserInputException
    except TaskIsOffloadedException:
        await agent_progress.complete_remaining_actions(ActionStatus.COMPLETED)
        raise
    finally:
        metrics.count("ModelFallbackCount", fallback_count)

        # We have finished running the program, any remaining actions should be marked as failed
        if not is_pausing_for_user_input:
            await agent_progress.complete_remaining_actions(ActionStatus.FAILED)

        executing_program_text = "Did not finish code executor program. Program unavailable."
        if executing_program:
            executing_program_text = executing_program.text
        snapshotter.write(
            "code_executor_program_guidance_data.jsonl",
            [
                GuidanceProgramS3SnapshotData(
                    prompt=json.dumps(code_executor_program.text),
                    program=json.dumps(executing_program_text),
                    model=llm_model,
                )
            ],
        )

        code_exec_rounds = agent.code_exec_rounds
        if current_code_exec_round:
            code_exec_rounds.append(current_code_exec_round)
        snapshotter.write(
            CODE_EXEC_STEPS_DATE_FILE_NAME,
            CodeExecStepsData(
                code_exec_steps=code_exec_rounds,
            ),
        )


def _contact_agent_uncertainty_check(run_output: RunOutput):
    start_index_of_contact_agent_uncertainty = run_output.error_str.find(
        _PREFIX_FOR_CONTACTS_AGENT_UNCERTAINTY
    )
    if start_index_of_contact_agent_uncertainty != -1:
        end_index_of_contact_agent_uncertainty = start_index_of_contact_agent_uncertainty + len(
            _PREFIX_FOR_CONTACTS_AGENT_UNCERTAINTY
        )
        msg_for_user = run_output.error_str[end_index_of_contact_agent_uncertainty:]
        raise ContactAgentUncertaintyException(message=msg_for_user)


def _code_run_timeout_check(run_output_str: str):
    if "Execution timed out." in run_output_str:
        raise CodeRunTimeoutException()


async def _get_new_code_exec_program(agent: Agent, llm_config_to_use: LLMConfig, few_shots: list):
    return await code_executor_program(
        llm=LLMFactory.create(llm_config=llm_config_to_use),
        tools=tools,
        plan=agent.plan,
        constitution=CODE_EXECUTOR_CONSTITUTION,
        user_details=get_user_details_prompt_message(agent.user_details),
        few_shots=few_shots,
        task=agent.task,
        previous_rounds=agent.code_exec_rounds,
        silent=True,
        async_mode=True,
    )