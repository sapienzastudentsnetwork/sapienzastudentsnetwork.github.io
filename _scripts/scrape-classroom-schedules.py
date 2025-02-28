import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def generate_time_slots():
    """
    Generates 30-minute slots from 08:00 to 19:00.
    """
    slots = []
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("19:00", "%H:%M")
    while start_time < end_time:
        next_time = start_time + timedelta(minutes=30)
        slots.append(f"{start_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}")
        start_time = next_time
    return slots

def split_schedule(schedule):
    """
    Normalizes the schedule by splitting larger intervals into 30-minute segments.
    For each day, we take the original keys and "expand" them into 30-minute segments.
    """
    normalized_schedule = {day: {slot: "" for slot in generate_time_slots()} for day in schedule.keys()}
    for day, times in schedule.items():
        for time_range, activity in times.items():
            if activity:
                start, end = time_range.split("-")
                current_time = datetime.strptime(start, "%H:%M")
                end_time = datetime.strptime(end, "%H:%M")
                while current_time < end_time:
                    next_time = current_time + timedelta(minutes=30)
                    slot = f"{current_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                    normalized_schedule[day][slot] = activity
                    current_time = next_time
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
    url = "https://gomppublic.uniroma1.it/ScriptService/OffertaFormativa/Ofs.6.0/AuleOrariScriptService/GenerateOrarioAula.aspx"

    tz = pytz.timezone("Europe/Rome")
    start_day = datetime.now(tz)

    # Adjust start_day to Monday if start_day is Saturday (5) or Sunday (6)
    if start_day.weekday() >= 5:
        days_until_monday = 7 - start_day.weekday()
        start_day += timedelta(days=days_until_monday)

    # Determine the week's Monday and Friday
    start_of_week = start_day - timedelta(days=start_day.weekday())  # Get Monday of the current week
    end_of_week = start_of_week + timedelta(days=4)  # Get Friday of the same week

    start_date = start_of_week.strftime("%Y/%m/%d")
    date_range = f"{start_of_week.strftime('%A %d %B %Y')} - {end_of_week.strftime('%A %d %B %Y')}"

    # Mapping of days from Italian to English
    days_mapping = {
        "Lunedì": "monday",
        "Martedì": "tuesday",
        "Mercoledì": "wednesday",
        "Giovedì": "thursday",
        "Venerdì": "friday"
    }

    common_params = {
        # "aulaUrl": "",
        # "annoAccademico": "2024/2025",
        # "virtuale": False,
        # "timeSlots": None,
        "displayMode": "OnlyAule",
        # "showTimeBar": True,
        "startDate": start_date
        #"showStyles": True,
        #"codiceAulaTagName": "",
        #"nomeAulaCssClass": "",
        #"oraInizioCssClass": "",
        #"oraFineCssClass": "",
        #"nomeEdificioCssClass": ""
    }

    classrooms = {
        "T1": "RM113-E01PTEL001",
        "S1": "RM113-E01PINL001"
    }

    for room_name, codice_interno in classrooms.items():
        params = {"controlID": "schedule", "codiceInterno": codice_interno}
        params.update(common_params)
        query_params = {"params": json.dumps(params), "_": "1740587354948"}
        response = requests.get(url, params=query_params)

        if response.status_code == 200:
            # Extract HTML content from the response
            match = re.search(r'\.html\("(.+?)"\);', response.content.decode('utf-8'), re.DOTALL)
            html_content = match.group(1).encode('utf-8').decode('unicode_escape') if match else ""
            soup = BeautifulSoup(html_content, 'html.parser')

            # Identify the header row containing the days of the week
            header_row = next((tr for tr in soup.find_all('tr') if tr.find('th', class_='Orario')), None)
            days = [th.get_text(strip=True) for th in header_row.find_all('th')[1:]] if header_row else []
            if len(days) > 2:
                days.pop()
                days.pop()

            # Initialize the schedule dictionary
            schedule = {days_mapping[day]: {} for day in days if day in days_mapping}
            for row in soup.find_all('tr'):
                timeslot_cell = row.find('td', class_='orario')
                if timeslot_cell:
                    timeslot = "-".join(timeslot_cell.stripped_strings)
                    cells = row.find_all('td')[1:]
                    for day, cell in zip(days, cells):
                        if day in days_mapping:
                            schedule[days_mapping[day]][timeslot] = " ".join(cell.stripped_strings)

            # Normalize the schedule into 30-minute segments
            normalized_schedule = split_schedule(schedule)
            # Apply merging: only slots with inconsistencies remain as half-hour slots,
            # while others (i.e., if for every day the slot is empty or contains the same event for the whole hour)
            # are merged into a single one-hour block.
            final_schedule = merge_time_slots(normalized_schedule)

            output_data = {"date_range": date_range, "timetables": final_schedule}

            # Save the result in a JSON file
            with open(f"../data/timetables_classrooms_{room_name}.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    get_classroom_schedule()
