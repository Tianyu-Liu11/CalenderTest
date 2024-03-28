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

# refresh and reload the fucntion
import importlib
import GPT_4_generated_code


def get_calendar_data(DATA_PATH):
    return pd.read_csv(DATA_PATH + "calendar_data.csv")

def get_question(DATA_PATH):
    with open(DATA_PATH + "question.json") as json_file:
        json_data = json.load(json_file)
    return json_data
    
    
def get_prompt(question):
    
    text = f"""{question}
    """
    
    PROMPT = f"""You are provided a DataFrame ```calendar_data(ID, status, summary, start, end , duration, attendees)```. This dataframe includes all you calenders.
    Your task is generate python function to query this dataframe and answer the question. Output a python function object without any prefix instructionn and explaination.

    The input have following columns:
    - ID: meeting ID;
    - status: meeting status, including the following status: cancelled, confirmed, tentative;
    - summary: meeting or event topic;
    - start: the start date of meeting, date format: YYYY-MM-DD hh:mm:ss.fff-zz:xx. for example "2024-02-05 12:00:00-00:00";
    - end: the start date of meeting, date format: YYYY-MM-DD hh:mm:ss.fff-zz:xx, for example "2024-02-05 13:00:00-00:00";
    - duration: meeting duration (second);
    - attendees: people who attend the meeting delimited by by the line terminator.

    Output using the folowing format:
    code language: python
    function name: query():
    input: calendar_data
    output is a executable python function without any prefix instructionn and explaination. If any python packages are required, add it.

    Today's date is '2024-03-12 13:02:30-03:20'.

    For example, the output only have the following format:
    import pandas as pd 
    def query(calendar_data):
        return calendar_data[0]

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

# generated_code = get_completion(MODEL, PROMPT)
# print(generated_code)

def generate_code(CODE_PATH = "/generated_code", MODEL="gpt-4"):
    if MODEL == "gpt-4":
        FILE_NAME = 'GPT_4_generated_code.py'
    else: # MODEL = "gpt-3.5-turbo"
        FILE_NAME = 'gpt_3.5_turbo_generated_code.py'

    fp = open(FILE_NAME, 'w')
    # Add package dependency, eg import panda as pd 
    fp.write(generated_code)
    fp.close()




# Import your module


# Must update the function 
importlib.reload(GPT_4_generated_code)

count_correct, count_incorrect, count_code_error = 0, 0, 0

try:
    answer = GPT_4_generated_code.query(calendar_data)
except:
    # count how many unexecutable code OR incorrect answer we get.
    # count_code_error += 1
    pass
print(answer)





def main():
    # argparse 
    DATA_PATH = "../data/"
    MODEL = "gpt-4"
    # MODEL = "gpt-3.5-turbo"
    
    
    
    
    calendar_Data = get_calendar_data(DATA_PATH=DATA_PATH)





if __name__ == '__main__':
    main()