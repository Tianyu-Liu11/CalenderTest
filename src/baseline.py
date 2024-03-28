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




def get_code_completion(MODEL, PROMPT):

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







def main():
    # Add argparse and *karg
    
    DATA_PATH = "./data/"
    MODEL = "gpt-4"
    # MODEL = "gpt-3.5-turbo"
    
    print(DATA_PATH + "calendar_data.csv")
    
    result = {'success': 0, 'wrong_answer': 0, 'error': 0}
    generated_code_analysis = {'question': '', 
                               'python_with_code': '',
                               'answer': ''
                               }
    
    # run()
    # print('END')
    
    calendar_data = get_calendar_data(DATA_PATH=DATA_PATH)
    queston_answer_pairs = get_question(DATA_PATH=DATA_PATH)
    calendar_data_JSON = calendar_data.to_json() 
    
    ground_true = []
    
    for i in range(10):
        # print(f"""question index {i} \n""")
        print(f"""Question: {queston_answer_pairs[i]['question']}\n True answer: {queston_answer_pairs[i]['answer']}""")
        
        PROMPT = get_prompt(queston_answer_pairs[i]['question'], calendar_data_JSON)
        
        question = queston_answer_pairs[i]['question']
        ground_true = (queston_answer_pairs[i]['answer'])
        
        llm_reply_with_code = get_code_completion(MODEL, PROMPT)
        print(f"""The answer of LLM: {llm_reply_with_code}""")
        
        # # extract code from the output of LLM
        # _python_code_re_pattern = "```python\n(.*?)```"
        # llm_reply_without_code = re.sub(
        #             _python_code_re_pattern, "", llm_reply_with_code, flags=re.DOTALL
        #             )
        # python_code_list = re.findall(_python_code_re_pattern, llm_reply_with_code, re.DOTALL)
    

    
        
    # result = json.dumps(result)
    print(result)
        # save the code and result into .json 

    # result = {'success': 0, 'wrong_answer': 0, 'error': 0}
    # generated_code_analysis = {'question': '', 
    #                            'python_with_code': '',
    #                            'answer': ''
    #                            }


    # for code, queston_answer_pair in (python_code_list, queston_answer_pairs):
    #     try:
    #         exec(code)
            
    #         try:
    #             answer # get from python code
    #         except NameError:
                 
    #     except:
    #         # 
    #         print()
    #         pass
        
        


if __name__ == '__main__':
    main()
    
    
    