def query(calendar_data):
    today_date = "2024-03-12"
    today_events = calendar_data[(calendar_data['start'].str.contains(today_date)) & (calendar_data['status'] == 'confirmed')].count()
    return today_events['ID']