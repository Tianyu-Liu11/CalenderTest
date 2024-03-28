```python
import pandas as pd

def events_scheduled_today(df):
    #Convert start column to datetime 
    df['start'] = pd.to_datetime(df['start'])
    today = pd.to_datetime('2024-03-12')
    #Filtering DataFrame to only include rows where start date is today
    df = df[df['start'].dt.date == today.date()]
    return df.shape[0]

events_today = events_scheduled_today(calendar_data)
```