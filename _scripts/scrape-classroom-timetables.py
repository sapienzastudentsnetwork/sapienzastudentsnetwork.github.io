import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import urllib3
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_time_slots(start_str="08:00", end_str="19:30"):
    """
    Generates 30-minute slots between start_str and end_str.
    """
    slots = []
    start_time = datetime.strptime(start_str, "%H:%M")
    end_time = datetime.strptime(end_str, "%H:%M")
    while start_time < end_time:
        next_time = start_time + timedelta(minutes=30)
        slots.append(f"{start_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}")
        start_time = next_time
    return slots

def split_schedule(schedule, start_str="08:00", end_str="19:30"):
    """
    Normalizes the schedule by splitting larger intervals into 30-minute segments.
    For each day, we take the original keys and "expand" them into 30-minute segments.
    Dynamically includes any slots (like 19:30-20:00) if they are actually used.
    """
    # Base slots 08:00-19:30
    base_slots = generate_time_slots(start_str, end_str)
    # To collect any additional slots (like '19:30-20:00') that appear in the data
    extra_slots = set()

    # First pass to find all time ranges actually used (including potential overflow)
    expanded_times = {}
    for day, times in schedule.items():
        expanded_times[day] = {}
        for time_range, activity in times.items():
            if activity:
                start, end = time_range.split("-")
                current_time = datetime.strptime(start, "%H:%M")
                end_time = datetime.strptime(end, "%H:%M")
                while current_time < end_time:
                    next_time = current_time + timedelta(minutes=30)
                    slot = f"{current_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                    expanded_times[day][slot] = activity
                    if slot not in base_slots:
                        extra_slots.add(slot)
                    current_time = next_time

    # Now build the full list of slots for normalization
    all_slots = base_slots + sorted(extra_slots)

    # Build normalized schedule
    normalized_schedule = {day: {slot: "" for slot in all_slots} for day in schedule.keys()}
    for day in expanded_times:
        for slot, activity in expanded_times[day].items():
            normalized_schedule[day][slot] = activity

    return normalized_schedule

def merge_time_slots(normalized_schedule):
    """
    For each pair of 30-minute slots (i.e., for each hour), it checks:
      - If, for every day, both slots are empty,
        or (if not empty) they contain the same event (a one-hour event),
        then the two slots are merged into a single one-hour timeslot.
      - Otherwise, if in at least one day the two half-hours are "inconsistent"
        (i.e., only one half is occupied or they are occupied by different events),
        then the 30-minute slot division is maintained for all days.
    """
    # Retrieve the ordered list of 30-minute slots (same for all days)
    half_hour_slots = list(next(iter(normalized_schedule.values())).keys())
    new_schedule = {day: {} for day in normalized_schedule}
    i = 0
    while i < len(half_hour_slots):
        slot1 = half_hour_slots[i]
        if i + 1 < len(half_hour_slots):
            slot2 = half_hour_slots[i+1]
            can_merge = True
            for day in normalized_schedule:
                val1 = normalized_schedule[day][slot1]
                val2 = normalized_schedule[day][slot2]
                # If for a day one slot is empty and the other is not,
                # or if both are non-empty but different, they cannot be merged.
                if not ((val1 == "" and val2 == "") or (val1 == val2 and val1 != "")):
                    can_merge = False
                    break
            if can_merge:
                # Merge the two slots into a one-hour interval
                start_time = slot1.split("-")[0]
                end_time = slot2.split("-")[1]
                merged_slot = f"{start_time}-{end_time}"
                for day in normalized_schedule:
                    # Since if non-empty, val1 and val2 are equal, we can take either one
                    new_schedule[day][merged_slot] = normalized_schedule[day][slot1] or normalized_schedule[day][slot2]
                i += 2
            else:
                # Keep the 30-minute slot division for all days
                for day in normalized_schedule:
                    new_schedule[day][slot1] = normalized_schedule[day][slot1]
                    new_schedule[day][slot2] = normalized_schedule[day][slot2]
                i += 2
        else:
            # If there is an odd slot remaining, add it as is
            for day in normalized_schedule:
                new_schedule[day][slot1] = normalized_schedule[day][slot1]
            i += 1
    return new_schedule

def get_classroom_schedule():
    """
    Retrieves and processes classroom schedules from the university website.
    """
    url = "https://gomp.uniroma1.it/PublicFunctions/GestioneAule/JsonData/JsonData.aspx"

    tz = pytz.timezone("Europe/Rome")
    start_day = datetime.now(tz)

    # Adjust start_day to Monday if start_day is Saturday (5) or Sunday (6)
    if start_day.weekday() >= 5:
        days_until_monday = 7 - start_day.weekday()
        start_day += timedelta(days=days_until_monday)

    # Determine the week's Monday, Friday, and Saturday
    start_of_week = start_day - timedelta(days=start_day.weekday())  # Get Monday of the current week
    end_of_week = start_of_week + timedelta(days=4)  # Get Friday of the same week
    saturday_of_week = start_of_week + timedelta(days=5) # Get Saturday for API showdate

    date_range = f"{start_of_week.strftime('%A %d %B %Y')} - {end_of_week.strftime('%A %d %B %Y')}"

    days_list = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    # Mapping of classrooms
    classrooms = {
        "T1": {
            "item": "70000b7b-daf3-4315-839c-3f4b0ab0e131",
            "cache": "db4e2600-d2f7-4074-b826-72d617ae3a33"
        },
        "S1": {
            "item": "3204f38e-7393-4457-a108-c048458d026a",
            "cache": "db4e2600-d2f7-4074-b826-72d617ae3a33"
        },
        "Colossus": {
            "item": "ee4a84e8-2137-4f3e-8027-aa805d04dfb4",
            "cache": "d479c0b4-386c-42ae-951b-c627f6733b82"
        },
        "HAL9000": {
            "item": "6c66a63a-760e-4760-8146-e4fb63317684",
            "cache": "db4e2600-d2f7-4074-b826-72d617ae3a33"
        }
    }

    os.makedirs("data", exist_ok=True)

    for room_name, guids in classrooms.items():
        query_params = {
            "method": "list",
            "item": guids["item"],
            "cache": guids["cache"],
            "annoCorso": "",
            "canale": "",
            "ShowAllUnaTantum": "false"
        }

        body_data = {
            "showdate": f"{saturday_of_week.month}/{saturday_of_week.day}/{saturday_of_week.year}",
            "viewtype": "week",
            "timezone": "2"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "application/json, text/javascript, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://gomp.uniroma1.it",
            "Referer": f"https://gomp.uniroma1.it/PublicFunctions/GestioneAule/SchedullerEditor.aspx?SchedulerCache={guids['cache']}&Aula={guids['item']}&StartDate={saturday_of_week.month}_{saturday_of_week.day}_{saturday_of_week.year}&AnnoCorso=&Canale=&CalendarMode="
        }

        response = requests.post(url, params=query_params, data=body_data, headers=headers, verify=False)

        if response.status_code == 200:
            # Extract JSON content from the response
            data = response.json()
            raw_events = data.get("events", [])

            # Initialize the schedule dictionary
            schedule = {day: {} for day in days_list}

            for ev in raw_events:
                if len(ev) < 12:
                    continue

                # ev[2] is start time, ev[3] is end time, ev[11] is title
                start_dt = datetime.strptime(ev[2], "%m/%d/%Y %H:%M")
                end_dt = datetime.strptime(ev[3], "%m/%d/%Y %H:%M")
                title = ev[11].strip()

                # Filter only events that fall in our target Mon-Fri week
                if start_of_week.date() <= start_dt.date() <= end_of_week.date():
                    weekday_idx = start_dt.weekday()
                    if weekday_idx < 5:
                        day_key = days_list[weekday_idx]
                        timeslot = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
                        schedule[day_key][timeslot] = title

            # Normalize the schedule into 30-minute segments
            if room_name in ["Colossus", "HAL9000"]:
                start_slot = "09:30"
                end_slot = "18:00"
            else:
                start_slot = "08:00"
                end_slot = "19:30"

            normalized_schedule = split_schedule(schedule, start_str=start_slot, end_str=end_slot)
            # Apply merging: only slots with inconsistencies remain as half-hour slots,
            # while others (i.e., if for every day the slot is empty or contains the same event for the whole hour)
            # are merged into a single one-hour block.
            final_schedule = merge_time_slots(normalized_schedule)

            output_data = {"date_range": date_range, "timetables": final_schedule}

            # Save the result in a JSON file
            with open(f"data/timetables_classrooms_{room_name}.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    get_classroom_schedule()