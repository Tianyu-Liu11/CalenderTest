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
    
    
    
def get_prompt(question):
    
    text = f"""{question}
    """
    
    PROMPT = f"""You are provided a Pandas dataframe named calendar_data, columns = [ID, status, summary, start, end , duration, attendees]. DataFrame calendar_data includes all you calenders. 
    Your task is generate python function to query this dataframe and answer the question. Output a python code block without any prefix instructionn and explaination. 
    Today's date is '2024-03-12 13:02:30-03:20'.

    The input have following columns:
    - ID: meeting ID;
    - status: meeting status, including the following status: cancelled, confirmed, tentative;
    - summary: meeting or event topic;
    - start: the start date of meeting, date format: YYYY-MM-DD hh:mm:ss.fff-zz:xx. for example "2024-02-05 12:00:00-00:00";
    - end: the start date of meeting, date format: YYYY-MM-DD hh:mm:ss.fff-zz:xx, for example "2024-02-05 13:00:00-00:00";
    - duration: meeting duration (second);
    - attendees: people who attend the meeting delimited by the line terminator within 1 sentence.

    Output is executable Python code by enclosing it in triple backticks:
    ```python
    <your code here>
    ```

    The input of python code is a Pandas dataframe named calendar_data, and the answer is saved in variable answer.

    For example, the output have the following format:
    ```
    import pandas as pd 
    def query(calendar_data):
        return calendar_data[0]
    answer = query(calendar_data)
    ```

    Question to be resolved: {text} 
    """
    
    return PROMPT




def get_code_completion(MODEL, PROMPT):
    
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": PROMPT,
            }
        ],
        model=MODEL,
    )

    # verify the output
    return chat_completion.choices[0].message.content







def main():
    # argparse 
    DATA_PATH = "../data/"
    MODEL = "gpt-4"
    # MODEL = "gpt-3.5-turbo"
    
    
    calendar_Data = get_calendar_data(DATA_PATH=DATA_PATH)
    queston_answer_pair = get_question(DATA_PATH=DATA_PATH)
    
    
    for i in range():
        get_prompt(queston_answer_pair[i]['question'])
        

    llm_reply_with_code = get_code_completion(MODEL, PROMPT)

    _python_code_re_pattern = "```python\n(.*?)```"
    llm_reply_without_code = re.sub(
                _python_code_re_pattern, "", llm_reply_with_code, flags=re.DOTALL
                )
    python_code_list = re.findall(_python_code_re_pattern, llm_reply_with_code, re.DOTALL)



if __name__ == '__main__':
    main()