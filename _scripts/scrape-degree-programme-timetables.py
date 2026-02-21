import os
import json
import re
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup


def extract_course_code(course_name):
    """
    Extracts the course ID and unit/module number from the course name.
    """
    # Extract the ID that starts with "AAF" followed by numbers or just a numeric ID
    match = re.match(r"(AAF\d+|\d+)", course_name)
    if not match:
        return None
    id_number = match.group(1)

    # Search for the unit or module number
    roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
    unit_number = None

    if "UNIT" in course_name:
        match = re.search(r"UNIT\s*(\d+)", course_name)
        if match:
            # e.g. "UNIT 1" -> "1"
            unit_number = match.group(1)
        else:
            match = re.search(r"UNIT\s*\b(\w+)", course_name)
            if match:
                # Convert Roman numerals to Arabic numbers, if necessary
                # e.g. "UNIT I" -> "1"
                unit_number = str(roman_to_int.get(match.group(1), match.group(1)))
    elif "MODULO" in course_name:
        match = re.search(r"\b(\w+)\s*MODULO", course_name)
        if match:
            # Convert Roman numerals to Arabic numbers, if necessary
            # e.g. "I MODULO" -> "1"
            unit_number = str(roman_to_int.get(match.group(1), match.group(1)))

    # If unit/module number is found, return with underscore; otherwise, just return the ID
    if unit_number:
        return f"{id_number}_{unit_number}"
    else:
        return id_number


def load_dict_from_json(source_file_name):
    """
    Loads a dictionary from a JSON file. If invalid, backs up the file.
    """
    if os.path.exists(source_file_name):
        try:
            # Try to open the file as JSON
            with open(source_file_name, "r") as file:
                dictionary_data = json.load(file)
                print(f"File '{source_file_name}' opened successfully and loaded as a dictionary.")
                return dictionary_data
        except json.JSONDecodeError:
            # If the file is not a valid JSON, rename the file by adding the .bak extension
            # with the current date and time to avoid overwriting it when it might not be desired
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_file_name = f"{source_file_name}.bak{current_time}"
            os.rename(source_file_name, new_file_name)
            print(f"The file '{source_file_name}' is not a valid JSON, renamed to '{new_file_name}'.")
    else:
        print(f"File '{source_file_name}' not found.")

    return {}


def escape_dict_double_quotes(input_dict) -> dict:
    """
    Converts dictionary to JSON string, escapes double quotes, and parses it back.
    """
    # Convert the input dictionary to a JSON-formatted string with 4-space indentation
    input_dict_json_string = json.dumps(input_dict, indent=4)
    # Use a regular expression to replace double quote characters within the JSON string
    # with escaped double quotes if they are not already escaped (not preceded by a backslash)
    input_dict_json_string = re.sub(r'(?<!\\)\\"', r'\\\\\\"', input_dict_json_string)
    # Return the resulting dictionary after parsing the JSON string
    return json.loads(input_dict_json_string)


def extract_timetables_and_teachers(DOM, semester, degree_programme_code, course_timetables_dict, teachers_dict):
    """
    Iterates through the HTML tables to extract class timetables and populate teachers and courses dictionaries.
    """
    # Hard-coded list of (course_code, channel, teacher_name) erroneous combinations to be ignored
    ignore_conditions = [
        # ("1015883", "1", "MASI IACOPO"),  # Ignore MASI IACOPO's class for course 1015883 on channel 1
        # ("10621297", "1", "PIPERNO ADOLFO")  # Ignore PIPERNO ADOLFO's class for course 1020420 on channel 1
    ]

    # Iterate through the tables and extract class timetables
    for div in DOM.find_all(class_='sommario'):
        h2_tag_text = div.find('h2').text

        if f"{semester} semestre" not in h2_tag_text:
           continue

        for h3 in div.find_all('h3'):
            # The h3 elements contain text in this format:
            # Canale <Unico/1/2/...>
            channel = h3.text.split()[-1] if h3.text.split()[-1] != "Unico" else '0'

            # The tables are expected to be organized in the following way:
            # Course and teacher info | Building and classroom info | Schedule
            # e.g.
            #      [0]
            #      101226 CALCOLO DIFFERENZIALE
            #         MARIO ROSSI
            #         LUIGI BIANCHI
            #
            #      [1]
            #      Edificio: CU006
            #      Aula III
            #
            #      [2]
            #      lunedì dalle 08:00 alle 11:00
            #      venerdì dalle 08:00 alle 10:00

            for tr in h3.find_next().find_all('tr')[1:]:
                (course_column, classroom_column, schedule_column) = tuple(tr.find_all('td'))

                # Find the <a> element containing the course's code
                course_code_link = course_column.find('a')
                # Extract the course code from the course name
                course_name = course_code_link.text
                course_code = extract_course_code(course_name)

                # Find the <a> element containing the teacher's name
                teacher_divs = course_column.find_all('div', class_='docente')
                course_teachers_dict = {}

                if teacher_divs:
                    for teacher_div in teacher_divs:
                        # Prepare to extract teacher data
                        teacher_a = teacher_div.find('a')
                        # Extract the teacher's name
                        teacher_name = teacher_a.text.strip()

                        # Check if the current combination of course_code, channel, and teacher_name should be ignored
                        if (course_code, channel, teacher_name) in ignore_conditions:
                            continue

                        # Extract the URL of the teacher's page
                        teacher_page_url = teacher_a['href']
                        # Extract the teacher's UID from the URL of the teacher's page
                        teacher_id = teacher_page_url.split('=')[-1]

                        if teacher_id not in teachers_dict:
                            teachers_dict[teacher_id] = {"name": teacher_name}
                        else:
                            teachers_dict[teacher_id]["name"] = teacher_name

                        course_teachers_dict[teacher_id] = teacher_name

                # Extract location information from column 1 of the table
                location = classroom_column
                # Search for matches for building and classroom in the location string
                building_match = re.search(r'Edificio: (\w+)', str(location), re.IGNORECASE)
                classroom_match = re.search(r'Aula ([\w\s\d]+)', str(location), re.IGNORECASE)

                # If matches for building and classroom are found
                if building_match and classroom_match:
                    # Extract the building name and remove extra spaces
                    building = re.sub(r'\s+', ' ', building_match.group(1)).strip()
                    # Extract the classroom name and remove extra spaces
                    classroom = re.sub(r'\s+', ' ', classroom_match.group(1)).strip()
                    # Create a new location string that combines building and classroom
                    location = f"Aula {classroom} (Edificio: {building})"
                else:
                    # If no matches are found, use the original text of the location
                    location = location.get_text()

                # Extract the classroom ID from the URL in the 'a' element in column 1
                classroom_id = classroom_column.find('a').get('href').replace("#aula_", "")

                # Extract class timings from the third column
                day_and_time_strings = str(schedule_column).replace("dalle ", "").replace("alle ", "").replace(":00", "")

                for day_and_time_string in day_and_time_strings.replace("<td> ", "").replace("</td>", "").split("<br/>"):
                    # e.g. lunedì dalle 08:00 alle 11:00
                    day_and_time_string_fields = day_and_time_string.split(" ")
                    schedule_day_name = day_and_time_string_fields[0]
                    schedule_start_time = day_and_time_string_fields[1]
                    schedule_end_time = day_and_time_string_fields[2]
                    schedule_time_slot = f"{schedule_start_time} - {schedule_end_time}"
                    schedule_time_slot = re.sub(r'\b0(\d)', r'\1', schedule_time_slot)

                    # 1055043 - STATISTICS is offered in both ACSAI and Cybersecurity, but with different professors and schedules
                    if course_code == "1055043" and degree_programme_code == "33516":
                        course_code = "1055043_2"

                    if course_code not in course_timetables_dict:
                        course_timetables_dict[course_code] = {
                            "subject": ' '.join(course_column.find('a').text.split()[1:]),
                            "degree": degree_programme_code,
                            "channels": {},
                            "code": course_column.find(class_='codiceInsegnamento').text
                        }

                        # 1041792 - Biometric Systems
                        # 1047622 - Cryptography
                        # 10589555 - Practical Network Defense
                        if course_code in ("1041792", "1047622", "10589555"):
                            course_timetables_dict[course_code]["degree"] = "33516"

                    if f"{channel}" not in course_timetables_dict[course_code]["channels"]:
                        course_timetables_dict[course_code]["channels"][f"{channel}"] = {}

                    if schedule_day_name not in course_timetables_dict[course_code]["channels"][f"{channel}"]:
                        # Create a new dictionary for the day name with class information for the channel
                        course_timetables_dict[course_code]["channels"][f"{channel}"][schedule_day_name] = [{
                            "teachers": course_teachers_dict,
                            "timeslot": schedule_time_slot,
                            "classrooms": {classroom_id: location}
                        }]
                    else:
                        # If the same schedule is already present, add the location to the list of classrooms
                        #
                        # Useful for courses that are held, by the same teacher,
                        # in more than one classroom at the same time slot (usually
                        # those in laboratories)
                        #
                        append_schedule = True
                        for day_schedule_entry_dict in course_timetables_dict[course_code]["channels"][f"{channel}"][schedule_day_name]:
                            if (day_schedule_entry_dict["teachers"] == course_teachers_dict) and (day_schedule_entry_dict["timeslot"] == schedule_time_slot):
                                if "classrooms" in day_schedule_entry_dict:
                                    day_schedule_entry_dict["classrooms"][classroom_id] = location
                                append_schedule = False
                                break

                        if append_schedule:
                            course_timetables_dict[course_code]["channels"][f"{channel}"][schedule_day_name].append({
                                "teachers": course_teachers_dict,
                                "timeslot": schedule_time_slot,
                                "classrooms": {classroom_id: location}
                            })

    # Sort days
    sort_days_order = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì"]
    for course_code, course_code_data in course_timetables_dict.items():
        sorted_channels = {}
        for channel, day_data in course_code_data["channels"].items():
            sorted_days = {day: day_data[day] for day in sort_days_order if day in day_data}
            sorted_channels[channel] = sorted_days
        course_timetables_dict[course_code]["channels"] = sorted_channels


def extract_raw_timetables_data(DOM):
    """
    Extracts raw scheduled timetable data from the HTML into a structured list.
    """
    data = []

    for div in DOM.find_all(class_='sommario'):
        year = {
            'year': div.find('h2').text,
            'channels': []
        }

        for h3 in div.find_all('h3'):
            channel = {
                'channel': h3.text,
                'timetable': []
            }

            for tr in h3.find_next().find_all('tr')[1:]:
                (course, room, schedule) = tuple(tr.find_all('td'))

                section = {
                    'course': course.find(class_='codiceInsegnamento').text,
                    'subject': ' '.join(course.find('a').text.split()[1:]),
                    'building': room.find('div').text,
                    'room': room.find('a').text,
                    'teachers': [teacher.text for teacher in course.find_all(class_='docente')] or [DOM.new_tag('p').text],
                    'schedule': []
                }

                for day_time in filter(lambda x: x.name != 'br', schedule.contents):
                    (day, _, from_, _, to) = day_time.split()
                    section['schedule'].append({
                        'day': day,
                        'from': from_,
                        'to': to
                    })

                channel['timetable'].append(section)
            year['channels'].append(channel)
        data.append(year)

    sort_days_order_dict = {
        "lunedì": 0, "martedì": 1, "mercoledì": 2, "giovedì": 3, "venerdì": 4, "sabato": 5, "domenica": 6
    }

    def sort_timetable_by_schedule_day(timetable):
        if timetable["schedule"]:
            return sort_days_order_dict[timetable["schedule"][0]["day"]]
        return float("inf")

    for entry in data:
        for channel in entry["channels"]:
            channel["timetable"].sort(key=lambda x: (x["course"], sort_timetable_by_schedule_day(x)))

    return data


def extract_classrooms(DOM, classrooms_dict):
    """
    Iterates through the classrooms table to extract location and map details.
    """
    # Get all the rows in the classrooms table except the first one (header)
    rows = DOM.find(class_='elenco_aule').find_all('tr')[1:]

    # Iterate through the table rows to extract classroom information
    # The tables is expected to be organized in the following way:
    # Brief description of the classroom | Classroom address info
    # e.g.
    #      [0]
    #      Aula 1 - Aule L Via del Castro Laurenziano 7a
    #
    #      [1]
    #      VIA del Castro Laurenziano, 7a ROMA presso Aule L Via del Castro Laurenziano 7a, Provincia di Roma mappa
    for row in rows:
        # Find the <a> tag within the row
        a_tag = row.find('a')
        if a_tag:
            # Extract the 'name' attribute and remove the 'aula_' prefix to get the classroom ID
            id = a_tag.get('name').replace('aula_', '')

            # Extract the classroom description and address, removing superfluous and/or repeated information
            td_tags = row.find_all('td')
            raw_description = td_tags[0].text
            description = raw_description.strip().split(" - Aule - Via")[0].split(" Via")[0]

            address = td_tags[1].text.strip().split(" ROMA ")[0]
            if "presso" in address:
                address = None

            # Change the first word so that only its first letter is capitalized
            # e.g. VIA del Castro Laurenziano, 7a -> Via del Castro Laurenziano, 7a
            address = (address.split()[0].capitalize() + ' ' + ' '.join(address.split()[1:])) if address else None

            # Default to "Viale Regina Elena, 295" as address for classrooms
            # having ' - Regina Elena - ' in description but no valid address
            #
            # e.g. Denominazione: AULA 101 - Regina Elena - Edificio D
            #      Indirizzo: , presso Regina Elena - Edificio D, Provincia di Roma
            #      ->
            #      description: AULA 101 - Regina Elena - Edificio D
            #      address: null
            #      ->
            #      address: Viale Regina Elena, 295
            if " - Regina Elena - " in description and address is None:
                address = "Viale Regina Elena, 295"
            if id == "cab0d0ee-1faa-4552-9587-7a559480dde4" and address is None:
                address = "Via Ariosto, 25"

            # Use a regular expression to replace multiple spaces with a single space
            if description:
                description = re.sub(r'\s+', ' ', description)

            if address:
                address = re.sub(r'\s+', ' ', address)

            # Extract the map link from the 'href' property of the 'a' element within the 'Address' cell
            map_a_tag = td_tags[1].find('a')

            if map_a_tag:
                map_link = map_a_tag.get('href')
            elif "Aule temporanee Via De Lollis" in raw_description:
                map_link = "https://maps.app.goo.gl/gxUJ8cNbmBPtiHcd9"
            elif address == "Via Ariosto, 25":
                map_link = "https://maps.app.goo.gl/WjRwtKmStfPfRwQF9"
            elif "Regina Elena - Edificio C" in description:
                map_link = "https://maps.app.goo.gl/6LEoK2i3SZqcW2gD6"
            elif "Regina Elena - Edificio D" in description:
                map_link = "https://maps.app.goo.gl/CSz17Qw3a4SfHT6n9"
            elif "Regina Elena - Edificio E" in description:
                map_link = "https://maps.app.goo.gl/vbt5p3VWWn8dWYka6"
            else:
                map_link = None

            # Create an information dictionary for this classroom
            classrooms_dict[id] = {
                "description": description,
                "address": address,
                "mapsUrl": map_link
            }


def apply_manual_overrides(course_timetables_dict, degree_programme_code):
    """
    Applies overrides for specific courses, teachers, and classrooms
    by reading from an external JSON configuration file.
    """
    overrides_file_path = "../data/timetables-overrides.json"
    overrides = load_dict_from_json(overrides_file_path)

    if not overrides:
        print(f"No overrides found in '{overrides_file_path}' or the file is empty.")
        return

    # Initialize missing courses
    # Retrieve the courses to add for the specific degree programme
    add_courses = overrides.get("add_courses", {}).get(degree_programme_code, {})
    for course_code, course_data in add_courses.items():
        if course_code not in course_timetables_dict:
            course_timetables_dict[course_code] = course_data

    # Add manual extra schedules
    add_schedules = overrides.get("add_schedules", {})
    for course_code, config in add_schedules.items():
        # Check if the override is limited to a specific degree programme
        limit_degree = config.get("degree_limit")
        if limit_degree and limit_degree != degree_programme_code:
            continue

        if course_code in course_timetables_dict:
            for channel, days in config.get("channels", {}).items():
                if channel not in course_timetables_dict[course_code]["channels"]:
                    course_timetables_dict[course_code]["channels"][channel] = {}

                for day, schedules in days.items():
                    if day not in course_timetables_dict[course_code]["channels"][channel]:
                        course_timetables_dict[course_code]["channels"][channel][day] = schedules

    # Override classrooms for specific days without altering teachers or timeslots
    if "change_classrooms" in overrides:
        for course_code, course_data in overrides["change_classrooms"].items():
            if course_code in course_timetables_dict:
                for channel, channel_data in course_data.get("channels", {}).items():
                    if channel in course_timetables_dict[course_code]["channels"]:
                        for day, new_classrooms in channel_data.items():
                            if day in course_timetables_dict[course_code]["channels"][channel]:
                                for schedule in course_timetables_dict[course_code]["channels"][channel][day]:
                                    schedule["classrooms"] = new_classrooms

    # Iterate through data for inline updates (teachers and classrooms)
    master_degrees = ("33508", "33516")
    add_teachers = overrides.get("add_teachers", {})
    replace_classrooms = overrides.get("replace_classrooms", {})
    remove_teachers = overrides.get("remove_teachers", {})

    for course_code, course_data in course_timetables_dict.items():
        course_degree = course_data.get("degree")

        # Skip courses that do not belong to the current degree programme,
        # unless both are master degrees
        if (
            course_degree != degree_programme_code
            and (degree_programme_code not in master_degrees or course_degree not in master_degrees)
        ):
            continue

        for channel_id, channel_data in course_data.get("channels", {}).items():
            for day_name, day_schedules in channel_data.items():
                filtered_day_schedules = []

                for day_schedule in day_schedules:
                    skip_schedule = False

                    # Remove invalid schedules based on specific dummy/empty teacher IDs
                    if "teachers" in day_schedule and course_code in remove_teachers:
                        for bad_teacher_id in remove_teachers[course_code]:
                            if bad_teacher_id in day_schedule["teachers"]:
                                # Skip this schedule entirely
                                skip_schedule = True
                                break

                    if skip_schedule:
                        continue

                    # Update or add teacher names if they match the override configuration
                    if "teachers" in day_schedule and course_code in add_teachers:
                        for teacher_id, new_name in add_teachers[course_code].items():
                            day_schedule["teachers"][teacher_id] = new_name

                    # Replace classroom details with custom info/URL mapping
                    if "classrooms" in day_schedule:
                        classroom_info = None
                        classroom_url = None

                        for room_id in day_schedule["classrooms"].keys():
                            if room_id in replace_classrooms:
                                classroom_info = replace_classrooms[room_id]["classroomInfo"]
                                classroom_url = replace_classrooms[room_id].get("classroomUrl")
                                # Apply the first found replacement and stop
                                break

                        if classroom_info:
                            # Remove the default 'classrooms' dict and use custom string fields
                            day_schedule.pop("classrooms")
                            day_schedule["classroomInfo"] = classroom_info
                            if classroom_url:
                                day_schedule["classroomUrl"] = classroom_url

                    filtered_day_schedules.append(day_schedule)

                # Apply the filtered and updated schedules back to the day
                channel_data[day_name] = filtered_day_schedules


def main():
    # Semester to scrape lesson timetables for
    semester = os.getenv("SEMESTER", "primo")

    # Degree program to scrape data for
    degree_programme_code = os.getenv("DEGREE_PROGRAMME_CODE", "33503")

    # Academic Year of the degree program to scrape data for
    academic_year = os.getenv("ACADEMIC_YEAR", "2025/2026")

    # Url of the gomppublic page containing timetables and classrooms for the specific degree program
    gomppublic_generateorario_url = os.getenv("GOMPPUBLIC_GENERATEORARIO_URL", 'https://gomppublic.uniroma1.it/ScriptService/OffertaFormativa/Ofs.6.0/AuleOrariScriptService/GenerateOrario.aspx?params={"controlID":"","aulaUrl":"","codiceInterno":{codiceInterno},"annoAccademico":"{annoAccademico}","virtuale":false,"timeSlots":null,"displayMode":"Manifesto","showStyles":false,"codiceAulaTagName":"","nomeAulaCssClass":"","navigateUrlInsegnamentoMode":"","navigateUrlInsegnamento":"","navigateUrlDocenteMode":"","navigateUrlDocente":"","repeatTrClass":""}&_=1702740827520')\
        .replace("{codiceInterno}", degree_programme_code)\
        .replace("{annoAccademico}", academic_year)

    # Classrooms data
    classrooms_file_name = "../data/classrooms.json"
    classrooms_dict = load_dict_from_json(classrooms_file_name)

    # Teachers data
    teachers_file_name = "../data/teachers.json"
    teachers_dict = load_dict_from_json(teachers_file_name)

    # Course timetables data
    course_timetables_file_name = "../data/timetables.json"
    course_timetables_dict = load_dict_from_json(course_timetables_file_name)

    # Scrape data
    DOM = BeautifulSoup(
        ' '.join(get(gomppublic_generateorario_url, verify=False).content[13:-3].decode('unicode-escape').split()),
        'html.parser'
    )

    extract_timetables_and_teachers(DOM, semester, degree_programme_code, course_timetables_dict, teachers_dict)

    raw_data = extract_raw_timetables_data(DOM)

    # Save the timetables to a JSON file
    with open(f"../data/timetables_raw_{degree_programme_code}_{academic_year.replace('/', '-')}.json", 'w') as rawTimetablesFile:
        json.dump(raw_data, rawTimetablesFile, indent=2, sort_keys=True)

    extract_classrooms(DOM, classrooms_dict)

    apply_manual_overrides(course_timetables_dict, degree_programme_code)

    # Save the classrooms information to a JSON file
    with open(f"../data/classrooms.json", 'w') as classroomsFile:
        json.dump(escape_dict_double_quotes(classrooms_dict), classroomsFile, indent=2)

    # Save the teachers information to a JSON file
    with open(f"../data/teachers.json", 'w') as teachersFile:
        json.dump(escape_dict_double_quotes(teachers_dict), teachersFile, indent=2)

    # Save the course timetables to a JSON file
    with open(f"../data/timetables.json", 'w') as timetablesFile:
        json.dump(escape_dict_double_quotes(course_timetables_dict), timetablesFile, indent=2)


if __name__ == '__main__':
    main()