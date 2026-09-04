import html
import requests
import json
import re
from datetime import datetime, timedelta
from urllib.parse import unquote
import pytz
import urllib3
import os

# Disable warnings emitted for requests made without TLS certificate verification.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Public GOMP endpoints used by the classroom timetable page.
# SchedaOrarioProgrammazione.aspx must be opened before JsonData.aspx because it
# creates the temporary scheduler cache required by the subsequent AJAX requests.
BASE_URL = "https://gomp.uniroma1.it/PublicFunctions/GestioneAule"
SCHEDULE_PAGE_URL = f"{BASE_URL}/SchedaOrarioProgrammazione.aspx"
JSON_DATA_URL = f"{BASE_URL}/JsonData/JsonData.aspx"

# Scheduler cache identifiers are GUIDs. Unlike classroom identifiers, cache IDs
# are temporary and must never be stored permanently in the classroom mapping.
GUID_PATTERN = r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"


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
    # Base slots for the configured opening interval.
    base_slots = generate_time_slots(start_str, end_str)

    # Collect any additional slots, such as 19:30-20:00, that occur in the
    # upstream data but fall outside the normal interval for the classroom.
    extra_slots = set()

    # First pass: expand every occupied interval into individual half-hour slots.
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

    # Build the complete ordered list used consistently for every weekday.
    all_slots = base_slots + sorted(extra_slots)

    # Initialize every slot as empty, then copy the expanded activities into it.
    normalized_schedule = {
        day: {slot: "" for slot in all_slots}
        for day in schedule.keys()
    }
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
    # Retrieve the ordered list of 30-minute slots, which is identical for all days.
    half_hour_slots = list(next(iter(normalized_schedule.values())).keys())
    new_schedule = {day: {} for day in normalized_schedule}
    i = 0

    while i < len(half_hour_slots):
        slot1 = half_hour_slots[i]
        if i + 1 < len(half_hour_slots):
            slot2 = half_hour_slots[i + 1]
            can_merge = True

            for day in normalized_schedule:
                val1 = normalized_schedule[day][slot1]
                val2 = normalized_schedule[day][slot2]

                # A pair cannot be merged if only one half is occupied or if the two
                # halves contain different activities on at least one weekday.
                if not ((val1 == "" and val2 == "") or (val1 == val2 and val1 != "")):
                    can_merge = False
                    break

            if can_merge:
                # Merge the two half-hour slots into a single one-hour interval.
                start_time = slot1.split("-")[0]
                end_time = slot2.split("-")[1]
                merged_slot = f"{start_time}-{end_time}"
                for day in normalized_schedule:
                    # If occupied, both halves contain the same value, so either one
                    # can provide the activity stored in the merged interval.
                    new_schedule[day][merged_slot] = (
                        normalized_schedule[day][slot1]
                        or normalized_schedule[day][slot2]
                    )
                i += 2
            else:
                # Keep both half-hour slots for every day to preserve column alignment.
                for day in normalized_schedule:
                    new_schedule[day][slot1] = normalized_schedule[day][slot1]
                    new_schedule[day][slot2] = normalized_schedule[day][slot2]
                i += 2
        else:
            # Preserve an unmatched final half-hour slot when the list has odd length.
            for day in normalized_schedule:
                new_schedule[day][slot1] = normalized_schedule[day][slot1]
            i += 1

    return new_schedule


def extract_cache_id(page_source):
    """
    Extracts the temporary scheduler cache identifier generated when the public
    classroom timetable page is opened.

    The identifier may appear in a normal query string, an HTML-escaped URL,
    a URL-encoded JavaScript string, or an inline JavaScript assignment.
    """
    decoded = html.unescape(page_source)

    # Decode twice to support values embedded in already encoded URLs or scripts.
    for _ in range(2):
        decoded = unquote(decoded)

    patterns = (
        rf"[?&]cache=({GUID_PATTERN})",
        rf"[?&]SchedulerCache=({GUID_PATTERN})",
        rf"[\"']cache[\"']\s*:\s*[\"']({GUID_PATTERN})",
        rf"\bcache\s*=\s*[\"']?({GUID_PATTERN})",
        rf"\bSchedulerCache\s*=\s*[\"']?({GUID_PATTERN})",
    )

    for pattern in patterns:
        match = re.search(pattern, decoded, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    # Failing explicitly prevents the scraper from reusing stale data or writing
    # empty timetable files when GOMP changes the page structure.
    raise RuntimeError("Unable to find the scheduler cache in the GOMP page")


def create_scheduler_session():
    """
    Opens the public timetable page and returns the initialized HTTP session and
    its freshly generated scheduler cache identifier.

    The same session must be reused for JsonData.aspx requests because the cache
    can be linked to cookies and temporary server-side state created by this page.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    })

    response = session.get(
        SCHEDULE_PAGE_URL,
        timeout=30,
        verify=False,
    )
    response.raise_for_status()

    return session, extract_cache_id(response.text)


def get_classroom_schedule():
    """
    Retrieves and processes classroom schedules from the university website.
    """
    tz = pytz.timezone("Europe/Rome")
    start_day = datetime.now(tz)

    # On Saturday or Sunday, target the following week so the published timetable
    # always refers to the next active Monday-Friday interval.
    if start_day.weekday() >= 5:
        days_until_monday = 7 - start_day.weekday()
        start_day += timedelta(days=days_until_monday)

    # Determine the target week's Monday, Friday, and Saturday. GOMP expects the
    # Saturday date in showdate to select the corresponding Monday-Friday week.
    start_of_week = start_day - timedelta(days=start_day.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    saturday_of_week = start_of_week + timedelta(days=5)

    date_range = (
        f"{start_of_week.strftime('%A %d %B %Y')} - "
        f"{end_of_week.strftime('%A %d %B %Y')}"
    )
    showdate = (
        f"{saturday_of_week.month}/"
        f"{saturday_of_week.day}/"
        f"{saturday_of_week.year}"
    )
    days_list = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    # Permanent classroom identifiers. Scheduler cache IDs are session-scoped
    # and are obtained from the public timetable page at runtime.
    classrooms = {
        "T1": "70000b7b-daf3-4315-839c-3f4b0ab0e131",
        "S1": "3204f38e-7393-4457-a108-c048458d026a",
        "Colossus": "ee4a84e8-2137-4f3e-8027-aa805d04dfb4",
        "HAL9000": "6c66a63a-760e-4760-8146-e4fb63317684",
    }

    # Initialize the scheduler once and reuse its session-scoped state for every
    # classroom request in this run.
    session, cache_id = create_scheduler_session()
    os.makedirs("data", exist_ok=True)

    try:
        for room_name, item_id in classrooms.items():
            query_params = {
                "method": "list",
                "item": item_id,
                "cache": cache_id,
                "annoCorso": "",
                "canale": "",
                "ShowAllUnaTantum": "false",
            }
            body_data = {
                "showdate": showdate,
                "viewtype": "week",
                "timezone": "2",
            }
            headers = {
                "Accept": "application/json, text/javascript, */*",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://gomp.uniroma1.it",
                "Referer": SCHEDULE_PAGE_URL,
            }

            # Reuse the initialized session so cookies and temporary server-side
            # scheduler state remain available throughout the request sequence.
            response = session.post(
                JSON_DATA_URL,
                params=query_params,
                data=body_data,
                headers=headers,
                timeout=30,
                verify=False,
            )
            response.raise_for_status()

            # Extract the JSON content returned by the GOMP scheduler endpoint.
            data = response.json()
            raw_events = data.get("events", [])

            # Initialize the schedule dictionary for the five displayed weekdays.
            schedule = {day: {} for day in days_list}
            for event in raw_events:
                if len(event) < 12:
                    continue

                # event[2] is the start time, event[3] is the end time, and
                # event[11] is the activity title shown in the timetable.
                start_dt = datetime.strptime(event[2], "%m/%d/%Y %H:%M")
                end_dt = datetime.strptime(event[3], "%m/%d/%Y %H:%M")
                title = event[11].strip()

                # Keep only events falling within the selected Monday-Friday week.
                if start_of_week.date() <= start_dt.date() <= end_of_week.date():
                    weekday_idx = start_dt.weekday()
                    if weekday_idx < 5:
                        day_key = days_list[weekday_idx]
                        timeslot = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
                        schedule[day_key][timeslot] = title

            # Colossus and HAL9000 use a shorter displayed interval than S1 and T1.
            if room_name in ("Colossus", "HAL9000"):
                start_slot = "09:30"
                end_slot = "18:00"
            else:
                start_slot = "08:00"
                end_slot = "19:30"

            # Normalize the schedule into 30-minute segments.
            normalized_schedule = split_schedule(
                schedule,
                start_str=start_slot,
                end_str=end_slot,
            )

            # Merge compatible adjacent slots. Only hours containing inconsistent
            # half-hour activities remain divided into 30-minute intervals.
            final_schedule = merge_time_slots(normalized_schedule)
            output_data = {
                "date_range": date_range,
                "timetables": final_schedule,
            }

            # Save the result only after the HTTP response and transformation have
            # completed successfully, preventing partial output on failure.
            output_path = f"data/timetables_classrooms_{room_name}.json"
            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(
                    output_data,
                    output_file,
                    indent=4,
                    ensure_ascii=False,
                )
    finally:
        session.close()


if __name__ == "__main__":
    get_classroom_schedule()
