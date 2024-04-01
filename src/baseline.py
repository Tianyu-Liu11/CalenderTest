"""
    Description:
"""

import os
import re
import json
import pandas as pd
import argparse
from openai import OpenAI
from dotenv import load_dotenv


def get_calendar_data(DATA_PATH):
    return pd.read_csv(DATA_PATH + "calendar_data.csv")


def get_question(DATA_PATH):
    with open(DATA_PATH + "question.json") as json_file:
        json_data = json.load(json_file)
    return json_data
    
    
    
def get_prompt(question, examples):
    
    task = f"""{question}
    """

    PROMPT = f"""Answer the following question based on the JSON file with agenda from Google Calendar.\n Question: {task}'
                \n\nJSON file with agenda:\n{examples}"""
                        
    return PROMPT




def get_completion(MODEL, PROMPT):

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content":PROMPT,
            }
        ],
        model=MODEL,
    )

    # verify the output
    return chat_completion.choices[0].message.content




def get_result_prompt(question, result):
    
    task = f"""{question}
    """

    PROMPT = f"""You are provided two answers: true answer and AI generated answer. Compare two answers, 
    if two answers are the same, return true; if two answers are different, return wrong;
    If AI generated answer didn't provide clear answer, for example the generated answer includes 'can not be determined' return 'Not determined'
    
    The true answer: {result['true_answer']}; The generated answer: {result['generated_answer']}.
    
    The output only consists of 'true', 'false' and 'not determined'
    """
                        
    return PROMPT




def main():
    # Add argparse and *karg
    
    DATA_PATH = "./data/"
    # MODEL = "gpt-4"
    MODEL = "gpt-3.5-turbo"
    
    print(DATA_PATH + "calendar_data.csv")
    
    result = {'success': 0, 'wrong_answer': 0, 'error': 0}
    question_answer_summary = {'question': '',
                               'true_answer':'', 
                               'generated_answer': ''
                               }
    result_list = []
    
    calendar_data = get_calendar_data(DATA_PATH=DATA_PATH)
    queston_answer_pairs = get_question(DATA_PATH=DATA_PATH)
    calendar_data_JSON = calendar_data.to_json() 
    
    ground_true = []
    
    for q_a_pair in queston_answer_pairs:

        # print(f"""Question: {q_a_pair['question']}\n True answer: {q_a_pair['answer']}""")
        
        PROMPT = get_prompt(q_a_pair['question'], calendar_data_JSON)
        
        # question = q_a_pair['question']
        # ground_true = (q_a_pair['answer'])
        
        llm_reply = get_completion(MODEL, PROMPT)
        # print(f"""The answer of LLM: {llm_reply}""")
        
        # result analysis
        question_answer_summary['question'] = q_a_pair['question']
        question_answer_summary['true_answer'] = q_a_pair['answer']
        question_answer_summary['generated_code'] = llm_reply
    
        result_list.append(question_answer_summary.copy())
 
 
 
 
#  

     
    for result in result_list:
        PROMPT_for_analysis = get_result_prompt(q_a_pair['question'], question_answer_summary)
        llm_result_analysis = get_completion(MODEL, PROMPT_for_analysis)
        print(llm_result_analysis)
        
         
        
    # result = json.dumps(result)
    print('End')
    # print(result)
    # save the code and result into .json 

    # result = {'success': 0, 'wrong_answer': 0, 'error': 0}
    # generated_code_analysis = {'question': '', 
    #                            'python_with_code': '',
    #                            'answer': ''
    #                            }


        
        


if __name__ == '__main__':
    main()
    
    
    