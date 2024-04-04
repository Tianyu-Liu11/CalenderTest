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
                \n\nJSON file with agenda:\n{examples}. Today's date is '2024-04-02 09:02:30' with date format '%Y-%m-%d %H:%M:%S'"""
                        
    return PROMPT




def get_completion(MODEL, PROMPT):

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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


# If two answers are the same, return true; 
# If two answers are different, return wrong; 
# If AI generated answer didn't provide clear answer, for example the generated answer includes 'can not be determined' return 'Not determined'

def main():
    # Add argparse and *karg
    
    
    DATA_PATH = "./data/"
    MODEL = "gpt-4"
    # MODEL = "ft:gpt-3.5-turbo-1106:ninjatech-ai-dev::8sQyzUKb"
    print(MODEL)
    
    # print(DATA_PATH + "calendar_data.csv")
    
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
    for i in range(5):
        
        result = {'success': 0, 'wrong_answer': 0, 'error': 0}
        for q_a_pair in queston_answer_pairs:

            # print(f"""Question: {q_a_pair['question']}\n True answer: {q_a_pair['answer']}""")
            
            PROMPT = get_prompt(q_a_pair['question'], calendar_data_JSON)
            
            # question = q_a_pair['question']
            # ground_true = (q_a_pair['answer'])
            
            llm_reply = get_completion(MODEL, PROMPT)
            # print(f"""The answer of LLM: {llm_reply}""")
            
            if str(q_a_pair['answer']) in llm_reply.lower():
                result['success'] += 1
            else:
                result['wrong_answer'] += 1
            
            # result analysis
            question_answer_summary['question'] = q_a_pair['question']
            question_answer_summary['true_answer'] = q_a_pair['answer']
            question_answer_summary['generated_code'] = llm_reply
        print(result)
        result_list.append(result.copy())   
    print(result_list)
    
    # with open('baseline_' + f"""{MODEL}""" + '_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(result_list, f, indent=4)    

    print('End')




if __name__ == '__main__':
    main()
    
    
    