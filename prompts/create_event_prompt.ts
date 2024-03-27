export const CREATE_EVENT_PROMPT = `
Date format: YYYY-MM-DDThh:mm:ss+00:00
Based on this event description: "Joey birthday tomorrow at 7 pm",
output a json of the following parameters: 
Today's datetime on UTC time 2023-05-02T10:00:00-00:00, it's Tuesday and timezone
of the user is -5, take into account the timezone of the user and today's date.
1. ID 
2. status 
3. summary 
4. start 
5. end 
6. duration
7. attendees
event_summary:
{{
    "ID": "mambf90j96gb0m3p8u9fo0q7v8",
    "status": "confirmed",
    "summary": "AI gateway",
    "start": "2024-02-05 12:00:00-08:00",
    "end": "2024-02-05 13:00:00-08:00",
    "duration": "3600.0",
    "attendees": "temp-testing@ninjatech.ai(accepted)\n yevhenia.spiridonova@ninjatech.ai(needsAction) Name: 40"
}}

Date format: YYYY-MM-DDThh:mm:ss-00:00
Based on this event description: "Create a meeting for 5 pm on Saturday with Joey",
output a json of the following parameters: 
Today's datetime on UTC time 2023-05-04T10:00:00+00:00, it's Thursday and timezone
of the user is -5, take into account the timezone of the user and today's date.
1. ID 
2. status 
3. summary 
4. start 
5. end 
6. duration
7. attendees
event_summary:
{{
    "ID": "mambf90j96gb0m3p8u9fo0q7v8",
    "status": "confirmed",
    "summary": "AI gateway",
    "start": "2024-02-05 12:00:00-08:00",
    "end": "2024-02-05 13:00:00-08:00",
    "duration": "3600.0",
    "attendees": "temp-testing@ninjatech.ai(accepted)\n yevhenia.spiridonova@ninjatech.ai(needsAction) Name: 40"
}}

Date format: YYYY-MM-DDThh:mm:ss-00:00
Based on this event description: "{query}", output a json of the
following parameters: 
Today's datetime on UTC time {date}, it's {dayName} and timezone of the user {u_timezone},
take into account the timezone of the user and today's date.
1. ID 
2. status 
3. summary 
4. start 
5. end 
6. duration
7. attendees
event_summary:
`