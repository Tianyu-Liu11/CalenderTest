def query(calendar_data):
    scheduled_meetings = calendar_data[calendar_data['status'] != 'cancelled']
    return len(scheduled_meetings)