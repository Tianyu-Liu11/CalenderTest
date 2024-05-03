# Code generation for filtration

## Dataset
Directory: CalendarTest

 - calendar_data.csv
   - A Pandas dataframe named calendar_data, columns = [ID, status, summary, start, end , duration, attendees], which consists of all the users calendar information; 
   - This dataframe consists of 20 meeting records

- question.json
  - Questions or tasks we use to evaluate the algorithm. Data format: JSON; Number of tasks: 46 tasks
  - "question": NL questions; 
  - "answer": ground truth answer, calculated manully based on the dataframe calendar_data

## Algorithms
- Baseline 1: GPT3.5+finetuned
- Baseline 2: GPT4
- Algorithm 1: GPT4+Prompt
- Algorithm 2: GPT4+Prompt


## Performance evaluation

- pass@1 accuracy

## Note on this project
- Calendar agent - Agenda_filtration()
https://www.notion.so/ninjatech-ai/Calendar-agent-Agenda_filtration-69b4e410f24b4f9f968df8fd3ab94f2a?pvs=4
- Summary agent_filtration()
https://www.notion.so/ninjatech-ai/Summary-agent_filtration-92913d98f727407bb265bf173ffe1ab1?pvs=4
