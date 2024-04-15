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
from datetime import datetime
import pandas as pd
from pandas import Timestamp, DataFrame
from datetime import timedelta


#    Not finished yet
# convert the start and end time into datetime format (%Y-%m-%d %H:%M:%S) to make it easier to generate code
def convert_date(calendar_data):   
    # Convert 'start' and 'end' columns to datetime objects
    # calendar_data['start'] = pd.to_datetime(calendar_data['start'])
    # calendar_data['end']   = pd.to_datetime(calendar_data['end'])
    # Format 'start' and 'end' columns into the desired string format
    calendar_data['start'] = calendar_data['start'].dt.strftime('%Y-%m-%d %H:%M:%S')
    calendar_data['end']   = calendar_data['end'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    calendar_data['start'] = pd.to_datetime(calendar_data['start'])
    calendar_data['end']   = pd.to_datetime(calendar_data['end'])
    # calendar_data['attendees'] = [ str(item) for item in calendar_data['attendees'] ]
    # weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # calendar_data['weekday'] =[ weekdays[pd.to_datetime(calendar_data["start"][i], format='%Y-%m-%d %H:%M:%S').weekday()] for i in range(len(calendar_data['start']))]
    
    return calendar_data


def main():
    df_as_dicts = [
        {'ID': 'd119c9af-4d0c-4d08-a1b6-344d02557345', 'status': 'confirmed', 'summary': 'Planning meeting', 'start': Timestamp('2023-10-02 09:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 10:00:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': 'janesmith@example.com(needsAction)\njoshrock@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': 'a115b615-fd92-4397-865c-ddd367b8d3bd', 'status': 'confirmed', 'summary': 'Strategy review', 'start': Timestamp('2023-10-02 10:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 12:00:00-0700', tz='America/Los_Angeles'), 'duration': 7200.0, 'attendees': 'janesmith@example.com(needsAction)\nleonardhill@example.com(needsAction)\nrichardx@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '4b3aae2a-193d-4fc4-957e-30fb429abe10', 'status': 'confirmed', 'summary': 'Lunch', 'start': Timestamp('2023-10-02 12:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 13:00:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': ''},
        {'ID': '79d54031-f8e9-4492-80bd-4fe34778e102', 'status': 'confirmed', 'summary': 'Manager 1 on 1', 'start': Timestamp('2023-10-02 13:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 14:00:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'richardx@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '43872aa1-2904-4e6e-88a7-2d4a7ed62bb9', 'status': 'confirmed', 'summary': 'Interview with candidate: John', 'start': Timestamp('2023-10-02 14:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 15:00:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': 'john@externalcompany.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '64de7fcc-448d-4445-8753-568eddfc47c1', 'status': 'confirmed', 'summary': 'Recruitment course', 'start': Timestamp('2023-10-02 16:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-02 17:30:00-0700', tz='America/Los_Angeles'), 'duration': 5400.0, 'attendees': 'hillary@recruitmentcourse.com(needsAction)\njanesmith@example.com(needsAction)\nrichardbaker@example.com(needsAction)\nterryterrence@example.com(needsAction)'},
        {'ID': 'b1a98166-7701-4f5f-82d0-ce9d4e3d1aa5', 'status': 'confirmed', 'summary': 'Interview with candidate: Sally', 'start': Timestamp('2023-10-03 09:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 10:00:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'sally@externalcompany.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '5690101a-5a43-47ca-be3e-545f6ae13bc3', 'status': 'confirmed', 'summary': 'Interview with candidate: Brent', 'start': Timestamp('2023-10-03 10:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 10:30:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'brent@externalcompany.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '833cc6ef-3ec8-4500-ba05-b7dc5a423f7a', 'status': 'confirmed', 'summary': 'Interview with candidate: Bob', 'start': Timestamp('2023-10-03 10:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 11:30:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': 'bob@externalcompany.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '516ec6dc-15a4-452e-93d2-c8050bb5439e', 'status': 'confirmed', 'summary': 'Lunch and learn: ethical recruiting', 'start': Timestamp('2023-10-03 12:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 13:00:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': 'janesmith@example.com(needsAction)\nkensmith@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '048df1ab-52f5-42d3-8c08-fd4665e83265', 'status': 'confirmed', 'summary': 'Interview with candidate: Alice', 'start': Timestamp('2023-10-03 13:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 13:30:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'alice@externalcompany.com(needsAction)\njanesmith@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': 'b9168d58-59a2-4fb1-b7d3-e364a3ab9dec', 'status': 'confirmed', 'summary': 'Interview with candidate: Jane', 'start': Timestamp('2023-10-03 13:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 14:00:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'jane@externalcompany.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': 'ffec807a-c51b-43bb-b9a8-f3bf31303dfb', 'status': 'confirmed', 'summary': 'Job fair: bob hill university', 'start': Timestamp('2023-10-03 14:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 16:00:00-0700', tz='America/Los_Angeles'), 'duration': 5400.0, 'attendees': ''},
        {'ID': 'e3e5aa3b-5646-41db-a9f0-6563fbd780ca', 'status': 'confirmed', 'summary': 'Recruitment analytics review', 'start': Timestamp('2023-10-03 16:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-03 17:00:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'janesmith@example.com(needsAction)\nrichardbaker@example.com(needsAction)'},
        {'ID': '2ee10fc7-88ef-4a3e-ad29-b0d4f52f355b', 'status': 'confirmed', 'summary': 'Online candidate search', 'start': Timestamp('2023-10-04 09:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-04 11:00:00-0700', tz='America/Los_Angeles'), 'duration': 7200.0, 'attendees': ''},
        {'ID': '5e5a1235-b1a4-449a-b2bf-a6604fa880e2', 'status': 'confirmed', 'summary': 'Interview with candidate: Stacy', 'start': Timestamp('2023-10-04 11:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-04 12:30:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': 'richardbaker@example.com(needsAction)\nstacy@externalcompany.com(needsAction)'},
        {'ID': '27215f76-ab8c-47c8-986f-fb92965e75c5', 'status': 'confirmed', 'summary': 'Lunch', 'start': Timestamp('2023-10-04 12:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-04 13:30:00-0700', tz='America/Los_Angeles'), 'duration': 3600.0, 'attendees': ''},
        {'ID': '39c217df-8138-4a9e-b219-f1af2574e738', 'status': 'confirmed', 'summary': 'Online candidate search', 'start': Timestamp('2023-10-04 14:00:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-04 16:00:00-0700', tz='America/Los_Angeles'), 'duration': 7200.0, 'attendees': ''},
        {'ID': 'bde5030b-698d-4378-abed-dd07a9621457', 'status': 'confirmed', 'summary': 'Job fair: alice smith university', 'start': Timestamp('2023-10-04 16:15:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-04 18:00:00-0700', tz='America/Los_Angeles'), 'duration': 6300.0, 'attendees': ''},
        {'ID': 'ee02de3c-502a-436f-9eda-7672570a80e3', 'status': 'confirmed', 'summary': 'Interview with candidate: Lenny', 'start': Timestamp('2023-10-05 09:30:00-0700', tz='America/Los_Angeles'), 'end': Timestamp('2023-10-05 10:00:00-0700', tz='America/Los_Angeles'), 'duration': 1800.0, 'attendees': 'richardbaker@example.com(needsAction)\nlenny@externalcompany.com(needsAction)'}
    ]
        
    calendar_data = DataFrame(df_as_dicts)  
    calendar_data = convert_date(calendar_data)
    print(calendar_data)

    def query_dataframe(filtered_calendar_data):
        # Step 1: Filter out cancelled meetings
        active_meetings = filtered_calendar_data[filtered_calendar_data['status'] != 'cancelled']
        
        # Step 2: Extract hour of the day from start times
        active_meetings['start_hour'] = active_meetings['start'].dt.hour
        
        # Step 3: Count meetings per hour
        meetings_per_hour = active_meetings['start_hour'].value_counts().sort_index()
        
        # Step 4: Identify the hour with the maximum number of meetings
        max_meetings_hour = meetings_per_hour.idxmax()
        
        # Retrieve count for the hour with the most meetings
        max_count = meetings_per_hour[max_meetings_hour]
        
        # Step 5: Return a DataFrame with the result
        result = pd.DataFrame({
            'Hour of Day': [max_meetings_hour],
            'Number of Meetings': [max_count]
        })
        
        return result


    walk_slots = query_dataframe(calendar_data)
    print(walk_slots)
    print("End")
   
   
   
   
   
   
        


if __name__ == '__main__':
    main()
    
    
    