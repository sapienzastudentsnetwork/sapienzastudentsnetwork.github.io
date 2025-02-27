import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def get_classroom_schedule():
    url = "https://gomppublic.uniroma1.it/ScriptService/OffertaFormativa/Ofs.6.0/AuleOrariScriptService/GenerateOrarioAula.aspx"

    tz = pytz.timezone("Europe/Rome")
    today = datetime.now(tz)

    # Adjust start_day to Monday if today is Saturday (5) or Sunday (6)
    if today.weekday() >= 5:
        days_until_monday = 7 - today.weekday()
        today += timedelta(days=days_until_monday)

    # Determine the week's Monday and Friday
    start_of_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    end_of_week = start_of_week + timedelta(days=4)  # Get Friday of the same week

    start_date = start_of_week.strftime("%Y/%m/%d")
    date_range = f"{start_of_week.strftime('%A %d %B %Y')} - {end_of_week.strftime('%A %d %B %Y')}"

    # Italian-to-English mapping for weekdays
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
            match = re.search(r'\.html\("(.+?)"\);', response.content.decode('utf-8'), re.DOTALL)
            html_content = match.group(1).encode('utf-8').decode('unicode_escape') if match else ""
            soup = BeautifulSoup(html_content, 'html.parser')

            header_row = next((tr for tr in soup.find_all('tr') if tr.find('th', class_='Orario')), None)
            days = [th.get_text(strip=True) for th in header_row.find_all('th')[1:]] if header_row else []
            if len(days) > 2:
                days.pop()
                days.pop()

            # Rename days from Italian to English
            schedule = {days_mapping[day]: {} for day in days if day in days_mapping}
            for row in soup.find_all('tr'):
                timeslot_cell = row.find('td', class_='orario')
                if timeslot_cell:
                    timeslot = "-".join(timeslot_cell.stripped_strings)
                    cells = row.find_all('td')[1:]
                    for day, cell in zip(days, cells):
                        if day in days_mapping:
                            schedule[days_mapping[day]][timeslot] = " ".join(cell.stripped_strings)

            output_data = {
                "date_range": date_range,
                "timetables": schedule
            }

            with open(f"../data/timetables_classrooms_{room_name}.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    get_classroom_schedule()
