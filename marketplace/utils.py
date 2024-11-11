from datetime import datetime, timedelta


def generate_time_choices(start_time="12:00 AM", end_time="11:45 PM", step_minutes=15):
    start = datetime.strptime(start_time, "%I:%M %p")
    end = datetime.strptime(end_time, "%I:%M %p")

    time_choices = []
    current_time = start

    while current_time <= end:
        time_choices.append((current_time.strftime("%I:%M %p"), current_time.strftime("%I:%M %p")))
        current_time += timedelta(minutes=step_minutes)

    return time_choices
