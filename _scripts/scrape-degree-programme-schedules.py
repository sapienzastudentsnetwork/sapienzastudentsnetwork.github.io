import os
import json
import re
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup


def extract_teaching_code(teaching_name):
    # Extract the numeric ID
    match = re.match(r"(\d+)", teaching_name)
    if not match:
        return None
    id_number = match.group(1)

    # Search for the unit or module number
    roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
    unit_number = None
    if "UNIT" in teaching_name:
        match = re.search(r"UNIT\s*(\d+)", teaching_name)
        if match:
            # e.g. "UNIT 1" -> "1"
            unit_number = match.group(1)
        else:
            match = re.search(r"UNIT\s*\b(\w+)", teaching_name)
            if match:
                # Convert Roman numerals to Arabic numbers, if necessary
                # e.g. "UNIT I" -> "1"
                unit_number = str(roman_to_int.get(match.group(1), match.group(1)))
    elif "MODULO" in teaching_name:
        match = re.search(r"\b(\w+)\s*MODULO", teaching_name)
        if match:
            # Convert Roman numerals to Arabic numbers, if necessary
            # e.g. "I MODULO" -> "1"
            unit_number = str(roman_to_int.get(match.group(1), match.group(1)))

    # If unit/module number is found, return with underscore; otherwise, just return the ID
    if unit_number:
        return f"{id_number}_{unit_number}"
    else:
        return id_number


def parse(DOM):
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
            # Teaching and teacher info | Building and classroom info | Schedule
            # e.g.
            #      [0]
            #      101226 CALCOLO DIFFERENZIALE
            #         MARIO ROSSI
            #
            #      [1]
            #      Edificio: CU006
            #      Aula III
            #
            #      [2]
            #      lunedì dalle 08:00 alle 11:00
            #      venerdì dalle 08:00 alle 10:00

            for tr in h3.findNext().find_all('tr')[1:]:
                (teaching_column, classroom_column, schedule_column) = tuple(tr.find_all('td'))
                
                # Find the <a> element containing the teaching's code
                teaching_code_link = teaching_column.find('a')

                # Extract the teaching code from the teaching name
                teaching_name = teaching_code_link.text
                teaching_code = extract_teaching_code(teaching_name)

                # Prepare to extract teacher data
                teacher_name     = None
                teacher_page_url = None

                # Find the <a> element containing the teacher's name
                teacher_div = teaching_column.find('div', class_='docente')

                if teacher_div:
                    teacher_a = teacher_div.find('a')

                    # Extract the teacher's name
                    teacher_name = teacher_a.text.strip()

                    # Extract the URL of the teacher's page
                    teacher_page_url = teacher_a['href']

                    # Extract the teacher's UID from the URL of the teacher's page
                    teacher_id = teacher_page_url.split('=')[-1]

                    if teacher_id not in teachers_dict:
                        teachers_dict[teacher_id] = {
                            "name": teacher_name,
                        }
                    else:
                        teachers_dict[teacher_id]["name"] = teacher_name
                else:
                    teacher_id = None

                # Extract location information from column 1 of the table
                location = classroom_column

                # Search for matches for building and classroom in the location string
                building_match = re.search(r'Edificio: (\w+)', str(location), re.IGNORECASE)
                classroom_match = re.search(r'Aula ([\w\s\d]+)', str(location), re.IGNORECASE)

                # If matches for building and classroom are found
                if building_match and classroom_match:
                    # Extract the building name and remove extra spaces
                    building = building_match.group(1)
                    building = re.sub(r'\s+', ' ', building).strip()

                    # Extract the classroom name and remove extra spaces
                    classroom = classroom_match.group(1)
                    classroom = re.sub(r'\s+', ' ', classroom).strip()

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

                    schedule_day_name   = day_and_time_string_fields[0]
                    schedule_start_time = day_and_time_string_fields[1]
                    schedule_end_time   = day_and_time_string_fields[2]
                    schedule_time_slot  = f"{schedule_start_time} - {schedule_end_time}"

                    if teaching_code not in teaching_schedules_dict:
                        teaching_schedules_dict[teaching_code] = {
                            "subject": ' '.join(teaching_column.find('a').text.split()[1:]),
                            "degree": degree_programme_code,
                            "channels": {},
                            "code": teaching_column.find(class_='codiceInsegnamento').text
                        }

                    if f"{channel}" not in teaching_schedules_dict[teaching_code]["channels"]:
                        teaching_schedules_dict[teaching_code]["channels"][f"{channel}"] = {}

                    if schedule_day_name not in teaching_schedules_dict[teaching_code]["channels"][f"{channel}"]:
                        # Create a new dictionary for the day name with class information for the channel
                        teaching_schedules_dict[teaching_code]["channels"][f"{channel}"][schedule_day_name] = [{
                            "teacher": teacher_id,
                            "timeslot": schedule_time_slot,
                            "classrooms": {
                                classroom_id: location
                            }
                        }]
                    else:
                        # If the same schedule is already present, add the location to the list of classrooms
                        #
                        # Useful for teachings that are held, by the same teacher,
                        # in more than one classroom at the same time slot (usually
                        # those in laboratories)
                        #

                        append_schedule = True

                        for day_schedule_entry_dict in teaching_schedules_dict[teaching_code]["channels"][f"{channel}"][schedule_day_name]:
                            if (day_schedule_entry_dict["teacher"] == teacher_id) and (day_schedule_entry_dict["timeslot"] == schedule_time_slot):
                                day_schedule_entry_dict["classrooms"][classroom_id] = location
                                append_schedule = False
                                break
                        
                        if append_schedule:
                            teaching_schedules_dict[teaching_code]["channels"][f"{channel}"][schedule_day_name].append({
                                "teacher": teacher_id,
                                "timeslot": schedule_time_slot,
                                "classrooms": {
                                    classroom_id: location
                                }
                            })

    # Sort days
    sort_days_order = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì"]

    for teaching_code, teaching_code_data in teaching_schedules_dict.items():
        sorted_channels = {}

        for channel, day_data in teaching_code_data["channels"].items():
            sorted_days = {day: day_data[day] for day in sort_days_order if day in day_data}
            sorted_channels[channel] = sorted_days

        teaching_schedules_dict[teaching_code]["channels"] = sorted_channels

    # ▀▀█▀▀ ▀█▀ ▒█▀▄▀█ ▒█▀▀▀ ▀▀█▀▀ ░█▀▀█ ▒█▀▀█ ▒█░░░ ▒█▀▀▀ ▒█▀▀▀█ ░ ░░░▒█ ▒█▀▀▀█ ▒█▀▀▀█ ▒█▄░▒█
    # ░▒█░░ ▒█░ ▒█▒█▒█ ▒█▀▀▀ ░▒█░░ ▒█▄▄█ ▒█▀▀▄ ▒█░░░ ▒█▀▀▀ ░▀▀▀▄▄ ▄ ░▄░▒█ ░▀▀▀▄▄ ▒█░░▒█ ▒█▒█▒█
    # ░▒█░░ ▄█▄ ▒█░░▒█ ▒█▄▄▄ ░▒█░░ ▒█░▒█ ▒█▄▄█ ▒█▄▄█ ▒█▄▄▄ ▒█▄▄▄█ █ ▒█▄▄█ ▒█▄▄▄█ ▒█▄▄▄█ ▒█░░▀█

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

            for tr in h3.findNext().find_all('tr')[1:]:
                (teaching, room, schedule) = tuple(tr.find_all('td'))

                section = {
                    'course': teaching.find(class_='codiceInsegnamento').text,
                    'subject': ' '.join(teaching.find('a').text.split()[1:]),
                    'building': room.find('div').text,
                    'room': room.find('a').text,
                    'teacher': (teaching.find(class_='docente') or DOM.new_tag('p')).text,
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

    # ▒█▀▀█ ▒█░░░ ░█▀▀█ ▒█▀▀▀█ ▒█▀▀▀█ ▒█▀▀█ ▒█▀▀▀█ ▒█▀▀▀█ ▒█▀▄▀█ ▒█▀▀▀█ ░ ░░░▒█ ▒█▀▀▀█ ▒█▀▀▀█ ▒█▄░▒█
    # ▒█░░░ ▒█░░░ ▒█▄▄█ ░▀▀▀▄▄ ░▀▀▀▄▄ ▒█▄▄▀ ▒█░░▒█ ▒█░░▒█ ▒█▒█▒█ ░▀▀▀▄▄ ▄ ░▄░▒█ ░▀▀▀▄▄ ▒█░░▒█ ▒█▒█▒█
    # ▒█▄▄█ ▒█▄▄█ ▒█░▒█ ▒█▄▄▄█ ▒█▄▄▄█ ▒█░▒█ ▒█▄▄▄█ ▒█▄▄▄█ ▒█░░▒█ ▒█▄▄▄█ █ ▒█▄▄█ ▒█▄▄▄█ ▒█▄▄▄█ ▒█░░▀█

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
            description = td_tags[0].text.strip().split(" - Aule - Via")[0].split(" Via")[0]

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

            # Use a regular expression to replace multiple spaces with a single space
            if description:
                description = re.sub(r'\s+', ' ', description)

            if address:
                address = re.sub(r'\s+', ' ', address)
            
            # Extract the map link from the 'href' property of the 'a' element within the 'Address' cell
            map_a_tag = td_tags[1].find('a')

            if map_a_tag:
                map_link = map_a_tag.get('href')
            else:
                map_link = None
            
            # Create an information dictionary for this classroom
            classrooms_dict[id] = {
                "description": description,
                "address": address,
                "mapsUrl": map_link
            }

    return data


def load_dict_from_json(source_file_name):
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


if __name__ == '__main__':
    # ▒█▀▀▀█ ▒█▀▀█ ▀▀█▀▀ ▀█▀ ▒█▀▀▀█ ▒█▄░▒█ ▒█▀▀▀█ 
    # ▒█░░▒█ ▒█▄▄█ ░▒█░░ ▒█░ ▒█░░▒█ ▒█▒█▒█ ░▀▀▀▄▄ 
    # ▒█▄▄▄█ ▒█░░░ ░▒█░░ ▄█▄ ▒█▄▄▄█ ▒█░░▀█ ▒█▄▄▄█

    # Semester to scrape teaching schedules for
    semester = os.getenv("SEMESTER", "primo")

    # Degree program to scrape data for
    degree_programme_code = os.getenv("DEGREE_PROGRAMME_CODE", "29923")

    # Academic Year of the degree program to scrape data for
    academic_year = os.getenv("ACADEMIC_YEAR", "2023/2024")

    # Url of the gomppublic page containing timetables and classrooms for the specific degree program
    gomppublic_generateorario_url = os.getenv("GOMPPUBLIC_GENERATEORARIO_URL")\
        .replace("{codiceInterno}", degree_programme_code)\
        .replace("{annoAccademico}", academic_year)

    # File to read and write classroom data to
    classrooms_file_name = "../data/classrooms.json"

    # File to read and write teacher data to
    teachers_file_name = "../data/teachers.json"

    # File to read and write teaching schedules info to
    teaching_schedules_file_name = "../data/schedules.json"

    #
    # ▒█░░░ ▒█▀▀▀█ ░█▀▀█ ▒█▀▀▄ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
    # ▒█░░░ ▒█░░▒█ ▒█▄▄█ ▒█░▒█ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
    # ▒█▄▄█ ▒█▄▄▄█ ▒█░▒█ ▒█▄▄▀ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
    #

    # Dictionary to store classroom information
    classrooms_dict = load_dict_from_json(classrooms_file_name)

    # Dictionary to store teacher info
    teachers_dict = load_dict_from_json(teachers_file_name)

    # Dictionary to store teaching schedules
    teaching_schedules_dict = load_dict_from_json(teaching_schedules_file_name)

    #
    # ▒█▀▀▀█ ▒█▀▀█ ▒█▀▀█ ░█▀▀█ ▒█▀▀█ ▒█▀▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
    # ░▀▀▀▄▄ ▒█░░░ ▒█▄▄▀ ▒█▄▄█ ▒█▄▄█ ▒█▀▀▀ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
    # ▒█▄▄▄█ ▒█▄▄█ ▒█░▒█ ▒█░▒█ ▒█░░░ ▒█▄▄▄ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
    #

    DOM = BeautifulSoup(
        ' '.join(get(gomppublic_generateorario_url).content[13:-3].decode('unicode-escape').split()),
        'html.parser'
    )

    #
    # ▒█▀▀▀ ▀▄▒▄▀ ▒█▀▀█ ▒█▀▀▀█ ▒█▀▀█ ▀▀█▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
    # ▒█▀▀▀ ░▒█░░ ▒█▄▄█ ▒█░░▒█ ▒█▄▄▀ ░▒█░░ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
    # ▒█▄▄▄ ▄▀▒▀▄ ▒█░░░ ▒█▄▄▄█ ▒█░▒█ ░▒█░░ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
    #

    # This function takes a Python dictionary, converts it to a JSON-formatted
    # string, escapes double quote characters within the JSON string, and then
    # parses the modified JSON string back into a Python dictionary

    def escape_dict_double_quotes(input_dict) -> dict:
        # Convert the input dictionary to a JSON-formatted string with 4-space indentation
        input_dict_json_string = json.dumps(input_dict, indent=4)

        # Use a regular expression to replace double quote characters within the JSON string
        # with escaped double quotes if they are not already escaped (not preceded by a backslash)
        input_dict_json_string = re.sub(r'(?<!\\)\\"', r'\\\\\\"', input_dict_json_string)

        # Return the resulting dictionary after parsing the JSON string
        return json.loads(input_dict_json_string)

    # Save the timetables to a JSON file
    with open(f'../data/timetables_{degree_programme_code}_{academic_year.replace('/', '-')}.json', 'w') as file:
        json.dump(parse(DOM), file, indent=2)

    # Save the classroom information to a JSON file
    with open(f"../data/classrooms.json", 'w') as classroomsFile:
        json.dump(escape_dict_double_quotes(classrooms_dict), classroomsFile, indent=2)

    # Save the teacher information to a JSON file
    with open(f"../data/teachers.json", 'w') as teachersFile:
        json.dump(escape_dict_double_quotes(teachers_dict), teachersFile, indent=2)

    # Save the teaching schedules to a JSON file
    with open(f"../data/schedules.json", 'w') as schedulesFile:
        json.dump(escape_dict_double_quotes(teaching_schedules_dict), schedulesFile, indent=2)