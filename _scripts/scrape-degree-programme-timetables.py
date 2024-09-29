import os
import json
import re
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup


def extract_course_code(course_name):
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


def parse(DOM):
    # Iterate through the tables and extract class timetables
    for div in DOM.find_all(class_='sommario'):
        h2_tag_text = div.find('h2').text

        if f"{semester} semestre" not in h2_tag_text:
           continue 

        # Hard-coded list of (course_code, channel, teacher_name) erroneous combinations to be ignored
        ignore_conditions = [
            # ("1015883", "1", "MASI IACOPO"),  # Ignore MASI IACOPO's class for course 1015883 on channel 1
            # ("1020420", "1", "PIPERNO ADOLFO")  # Ignore PIPERNO ADOLFO's class for course 1020420 on channel 1
        ]

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
            #
            #      [1]
            #      Edificio: CU006
            #      Aula III
            #
            #      [2]
            #      lunedì dalle 08:00 alle 11:00
            #      venerdì dalle 08:00 alle 10:00

            for tr in h3.findNext().find_all('tr')[1:]:
                (course_column, classroom_column, schedule_column) = tuple(tr.find_all('td'))
                
                # Find the <a> element containing the course's code
                course_code_link = course_column.find('a')

                # Extract the course code from the course name
                course_name = course_code_link.text
                course_code = extract_course_code(course_name)

                # Prepare to extract teacher data
                teacher_name     = None
                teacher_page_url = None

                # Find the <a> element containing the teacher's name
                teacher_div = course_column.find('div', class_='docente')

                if teacher_div:
                    teacher_a = teacher_div.find('a')

                    # Extract the teacher's name
                    teacher_name = teacher_a.text.strip()

                    # Check if the current combination of course_code, channel, and teacher_name should be ignored
                    if (course_code, channel, teacher_name) in ignore_conditions:
                        continue  # Skip processing if the condition matches

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
                    schedule_time_slot  = re.sub(r'\b0(\d)', r'\1', schedule_time_slot)

                    if course_code not in course_timetables_dict:
                        course_timetables_dict[course_code] = {
                            "subject": ' '.join(course_column.find('a').text.split()[1:]),
                            "degree": degree_programme_code,
                            "channels": {},
                            "code": course_column.find(class_='codiceInsegnamento').text
                        }

                    if f"{channel}" not in course_timetables_dict[course_code]["channels"]:
                        course_timetables_dict[course_code]["channels"][f"{channel}"] = {}

                    if schedule_day_name not in course_timetables_dict[course_code]["channels"][f"{channel}"]:
                        # Create a new dictionary for the day name with class information for the channel
                        course_timetables_dict[course_code]["channels"][f"{channel}"][schedule_day_name] = [{
                            "teacher": teacher_id,
                            "timeslot": schedule_time_slot,
                            "classrooms": {
                                classroom_id: location
                            }
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
                            if (day_schedule_entry_dict["teacher"] == teacher_id) and (day_schedule_entry_dict["timeslot"] == schedule_time_slot):
                                day_schedule_entry_dict["classrooms"][classroom_id] = location
                                append_schedule = False
                                break
                        
                        if append_schedule:
                            course_timetables_dict[course_code]["channels"][f"{channel}"][schedule_day_name].append({
                                "teacher": teacher_id,
                                "timeslot": schedule_time_slot,
                                "classrooms": {
                                    classroom_id: location
                                }
                            })

    # Sort days
    sort_days_order = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì"]

    for course_code, course_code_data in course_timetables_dict.items():
        sorted_channels = {}

        for channel, day_data in course_code_data["channels"].items():
            sorted_days = {day: day_data[day] for day in sort_days_order if day in day_data}
            sorted_channels[channel] = sorted_days

        course_timetables_dict[course_code]["channels"] = sorted_channels

    #  ▀▀█▀▀ ▀█▀ ▒█▀▄▀█ ▒█▀▀▀ ▀▀█▀▀ ░█▀▀█ ▒█▀▀█ ▒█░░░ ▒█▀▀▀ ▒█▀▀▀█ ░░ ▒█▀▀█ ░█▀▀█ ▒█░░▒█
    #  ░▒█░░ ▒█░ ▒█▒█▒█ ▒█▀▀▀ ░▒█░░ ▒█▄▄█ ▒█▀▀▄ ▒█░░░ ▒█▀▀▀ ░▀▀▀▄▄ ▀▀ ▒█▄▄▀ ▒█▄▄█ ▒█▒█▒█
    #  ░▒█░░ ▄█▄ ▒█░░▒█ ▒█▄▄▄ ░▒█░░ ▒█░▒█ ▒█▄▄█ ▒█▄▄█ ▒█▄▄▄ ▒█▄▄▄█ ░░ ▒█░▒█ ▒█░▒█ ▒█▄▀▄█

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
                (course, room, schedule) = tuple(tr.find_all('td'))

                section = {
                    'course': course.find(class_='codiceInsegnamento').text,
                    'subject': ' '.join(course.find('a').text.split()[1:]),
                    'building': room.find('div').text,
                    'room': room.find('a').text,
                    'teacher': (course.find(class_='docente') or DOM.new_tag('p')).text,
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

    # Semester to scrape lesson timetables for
    semester = os.getenv("SEMESTER", "primo")

    # Degree program to scrape data for
    degree_programme_code = os.getenv("DEGREE_PROGRAMME_CODE", "29923")

    # Academic Year of the degree program to scrape data for
    academic_year = os.getenv("ACADEMIC_YEAR", "2024/2025")

    # Url of the gomppublic page containing timetables and classrooms for the specific degree program
    gomppublic_generateorario_url = os.getenv("GOMPPUBLIC_GENERATEORARIO_URL", 'https://gomppublic.uniroma1.it/ScriptService/OffertaFormativa/Ofs.6.0/AuleOrariScriptService/GenerateOrario.aspx?params={"controlID":"","aulaUrl":"","codiceInterno":{codiceInterno},"annoAccademico":"{annoAccademico}","virtuale":false,"timeSlots":null,"displayMode":"Manifesto","showStyles":false,"codiceAulaTagName":"","nomeAulaCssClass":"","navigateUrlInsegnamentoMode":"","navigateUrlInsegnamento":"","navigateUrlDocenteMode":"","navigateUrlDocente":"","repeatTrClass":""}&_=1702740827520')\
        .replace("{codiceInterno}", degree_programme_code)\
        .replace("{annoAccademico}", academic_year)

    # File to read and write classroom data to
    classrooms_file_name = "../data/classrooms.json"

    # File to read and write teacher data to
    teachers_file_name = "../data/teachers.json"

    # File to read and write course timetables info to
    course_timetables_file_name = "../data/timetables.json"

    #
    # ▒█░░░ ▒█▀▀▀█ ░█▀▀█ ▒█▀▀▄ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
    # ▒█░░░ ▒█░░▒█ ▒█▄▄█ ▒█░▒█ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
    # ▒█▄▄█ ▒█▄▄▄█ ▒█░▒█ ▒█▄▄▀ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
    #

    # Dictionary to store classroom information
    classrooms_dict = load_dict_from_json(classrooms_file_name)

    # Dictionary to store teacher info
    teachers_dict = load_dict_from_json(teachers_file_name)

    # Dictionary to store course timetables
    course_timetables_dict = load_dict_from_json(course_timetables_file_name)

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
    with open(f"../data/timetables_raw_{degree_programme_code}_{academic_year.replace('/', '-')}.json", 'w') as rawTimetablesFile:
        json.dump(parse(DOM), rawTimetablesFile, indent=2)

    # ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀█ █░░█ 　 ▀▀█▀▀ ░▀░ █▀▄▀█ █▀▀ ▀▀█▀▀ █▀▀█ █▀▀▄ █░░ █▀▀ █▀▀
    # ░░█░░ █▀▀ █░▀░█ █░░█ █░░█ █▄▄▀ █▄▄█ █▄▄▀ █▄▄█ 　 ░░█░░ ▀█▀ █░▀░█ █▀▀ ░░█░░ █▄▄█ █▀▀▄ █░░ █▀▀ ▀▀█
    # ░░▀░░ ▀▀▀ ▀░░░▀ █▀▀▀ ▀▀▀▀ ▀░▀▀ ▀░░▀ ▀░▀▀ ▄▄▄█ 　 ░░▀░░ ▀▀▀ ▀░░░▀ ▀▀▀ ░░▀░░ ▀░░▀ ▀▀▀░ ▀▀▀ ▀▀▀ ▀▀▀

    currentDate = datetime.now()

    if currentDate <= datetime(2024, 10, 5):
        zoom_register_it = "Zoom (registrarsi tramite questo link)"
        zoom_register_en = "Zoom (register using this link)"

        zoom_login_it = "Zoom (effettuare l'accesso tramite account Sapienza)"
        zoom_login_en = "Zoom (login with Sapienza account)"

        scienzebiochimiche_aulab = "Aula B Scienze Biochimiche (CU010)"
        scienzebiochimiche_building = "https://maps.app.goo.gl/FDurWQ4cwoQVqCn5A"

        reginaelena_edificiod_101 = "Aula 101 Regina Elena Ed. D (RM112)"
        reginaelena_edificiod_201 = "Aula 201 Regina Elena Ed. D (RM112)"
        reginaelena_edificiod_301 = "Aula 301 Regina Elena Ed. D (RM112)"
        reginaelena_edificiod = "https://maps.app.goo.gl/7MAGdzdLAbU3Tae7A"

        tba_classroom = "Classroom To Be Defined"

        if degree_programme_code == "29923":
            # 1022301 - INGEGNERIA DEL SOFTWARE
            # Start date: Wednesday, October 2nd, 2024
            course_timetables_dict["1022301"]["channels"]["0"].pop("lunedì")

            # 10596283 - ORGANIZZAZIONE E GESTIONE PER LO START-UP AZIENDALE
            # Bando: il corso inizierà appena sarà individuato il docente.
            course_timetables_dict["10596283"]["channels"] = {}

        elif degree_programme_code == "29932":
            # 10600495 - AUTOMATIC VERIFICATION OF INTELLIGENT SYSTEMS
            course_timetables_dict["10600495"]["channels"]["0"]["lunedì"] = [
              {
                "teacher": "2bf66397-ce7b-43e0-b640-ca1e45805df4",
                "timeslot": "14 - 16",
                "classrooms": {
                  "3204f38e-7393-4457-a108-c048458d026a": "Aula S1 (Edificio: RM113)"
                }
              }
            ]

            # 10589621 - ADVANCED MACHINE LEARNING
            course_timetables_dict["10589621"]["channels"]["0"].pop("giovedì")

            # 10596281 - AUTONOMOUS NETWORKING
            course_timetables_dict["10596281"]["channels"]["0"]["venerdì"][0]["classrooms"] = {}
            course_timetables_dict["10596281"]["channels"]["0"]["venerdì"][0]["classroomInfo"] = reginaelena_edificiod_101
            course_timetables_dict["10596281"]["channels"]["0"]["venerdì"][0]["classroomUrl"] = reginaelena_edificiod

            # 1041764 - BIG DATA COMPUTING
            course_timetables_dict["1041764"]["channels"]["0"]["mercoledì"][0]["classrooms"] = {}
            course_timetables_dict["1041764"]["channels"]["0"]["mercoledì"][0]["classroomInfo"] = tba_classroom

            # 1041792 - BIOMETRIC SYSTEMS
            course_timetables_dict["1041792"] = {
                "subject": "BIOMETRIC SYSTEMS",
                "degree": "29932",
                "channels": {
                  "0": {
                    "mercoled\u00ec": [
                      {
                        "teacher": "58c84b39-9448-4ec2-8d83-e89268086aef",
                        "timeslot": "13 - 15",
                        "classrooms": {
                          "b368dabe-4b63-4129-94bd-2c97ea916fd0": "Aula G50 (Edificio: RM115)"
                        }
                      }
                    ],
                    "gioved\u00ec": [
                      {
                        "teacher": "58c84b39-9448-4ec2-8d83-e89268086aef",
                        "timeslot": "8 - 11",
                        "classrooms": {
                          "b368dabe-4b63-4129-94bd-2c97ea916fd0": "Aula G50 (Edificio: RM115)"
                        }
                      }
                    ]
                  }
                },
                "code": "1041792"
            }

            # 10600490 - BLOCKCHAIN AND DISTRIBUTED LEDGER TECHNOLOGIES
            course_timetables_dict["10600490"]["channels"]["0"]["martedì"][0]["classrooms"] = {}
            course_timetables_dict["10600490"]["channels"]["0"]["martedì"][0]["classroomInfo"] = reginaelena_edificiod_201
            course_timetables_dict["10600490"]["channels"]["0"]["martedì"][0]["classroomUrl"] = reginaelena_edificiod

            # 1047622 - CRYPTOGRAPHY
            course_timetables_dict["1047622"]["channels"]["0"]["martedì"][0]["classrooms"] = {}
            course_timetables_dict["1047622"]["channels"]["0"]["martedì"][0]["classroomInfo"] = reginaelena_edificiod_301
            course_timetables_dict["1047622"]["channels"]["0"]["martedì"][0]["classroomUrl"] = reginaelena_edificiod

            # 1047624 - DISTRIBUTED SYSTEMS
            course_timetables_dict["1047624"]["channels"]["0"]["giovedì"][0]["classrooms"] = {}
            course_timetables_dict["1047624"]["channels"]["0"]["giovedì"][0]["classroomInfo"] = reginaelena_edificiod_301
            course_timetables_dict["1047624"]["channels"]["0"]["giovedì"][0]["classroomUrl"] = reginaelena_edificiod

            # 1047627 - FOUNDATIONS OF DATA SCIENCE
            course_timetables_dict["1047627"] = {
                "subject": "FOUNDATIONS OF DATA SCIENCE",
                "degree": "29932",
                "channels": {
                  "0": {
                    "luned\u00ec": [
                      {
                        "teacher": "c6ebe64b-d218-4bed-9643-8de250010478",
                        "timeslot": "10 - 13",
                        "classrooms": {
                          "625390f2-0bbb-4072-b866-50902fa1bad9": "Aula 2 (Edificio: RM018)"
                        }
                      }
                    ],
                    "venerd\u00ec": [
                      {
                        "teacher": "c6ebe64b-d218-4bed-9643-8de250010478",
                        "timeslot": "11 - 13",
                        "classrooms": {
                          "625390f2-0bbb-4072-b866-50902fa1bad9": "Aula 2 (Edificio: RM018)"
                        }
                      }
                    ]
                  }
                },
                "code": "1047627"
            }

            # 1047642 - SECURITY IN SOFTWARE APPLICATIONS
            course_timetables_dict["1047642"]["channels"]["0"]["mercoledì"][0]["classrooms"] = {}
            course_timetables_dict["1047642"]["channels"]["0"]["mercoledì"][0]["classroomInfo"] = tba_classroom

        elif degree_programme_code == "30786":
            # 10595536 - BUSINESS AND COMPUTER SCIENCE
            course_timetables_dict["10595536"]["channels"]["0"]["martedì"] = [
                 {
                   "teacher": "e6fe77e5-c77c-440c-a952-b674f6f30471",
                   "timeslot": "13 - 15",
                   "classrooms": {
                     "b368dabe-4b63-4129-94bd-2c97ea916fd0": "Aula G50 (Edificio: RM115)"
                   }
                 }
            ]

            # 10595546 - COMPUTER ARCHITECTURE
            # Tuesday class cancelled due to teaching mission.
            course_timetables_dict["10595546_1"]["channels"]["0"].pop("martedì")

        for course_code, course_data in course_timetables_dict.items():
            for channel_id, channel_data in course_data["channels"].items():
                for day_name, day_schedules in channel_data.items():
                    for day_schedule in day_schedules:
                        # 101226 - CALCOLO DIFFERENZIALE
                        # L'incarico docenza per il Canale A-L è assegnato al prof. Valeriano Aiello,
                        # non più, alla professoressa Garroni, diventata direttrice a Matematica.
                        if (course_code == "101226") and (channel_id == "1"):
                            if day_schedule["teacher"] == "5374367e-49df-4ff1-985b-ab4b4612e702":
                                day_schedule["teacher"] = None
                                day_schedule["teacherInfo"] = "AIELLO VALERIANO"

                        if "classrooms" in day_schedule:
                            for classroom_id, classroom_description in day_schedule["classrooms"].items():
                                classroom_info = day_schedule.get("classroomInfo", None)
                                classroom_url  = day_schedule.get("classroomUrl", None)

                                if "(Edificio: RM158)" in classroom_description:
                                    # CALCOLO DIFFERENZIALE - 101226 - Valeriano Aiello
                                    if (course_code == "101226") and (channel_id == "1"):
                                        classroom_info = "Zoom (passcode: calcolo)"
                                        classroom_url  = "https://uniroma1.zoom.us/j/88466867222?pwd=6EF4OsvAuLSn7jFlUakRbLNVUnwIIP.1"
                                    # FONDAMENTI DI PROGRAMMAZIONE - 1015883 - Andrea Sterbini, Daniele Friolo
                                    elif (course_code == "1015883") and (channel_id == "1"):
                                        if day_name == "martedì":
                                            classroom_info = "Zoom (martedì, passcode: Python)"
                                            classroom_url = "https://uniroma1.zoom.us/j/87054111782?pwd=nsTI9aqovtLbaGefCerbbcCh6zmIDC.1"

                                        elif day_name == "giovedì":
                                            classroom_info = "Zoom (giovedì, passcode: Python)"
                                            classroom_url = "https://uniroma1.zoom.us/j/88273989794?pwd=qrJ2LHVcvilCVdSHWZmo5x1oQ7xbBc.1"
                                    # METODI MATEMATICI PER L'INFORMATICA - 1020420 - Lorenzo Carlucci
                                    elif (course_code == "1020420") and (channel_id == "1"):
                                        if day_name == "martedì":
                                            classroom_info = "Zoom (martedì)"
                                            classroom_url  = "https://uniroma1.zoom.us/j/86508273035?pwd=u2Hti0cPt8bFmOtvQzOx6EalSfrA9R.1"

                                        elif day_name == "mercoledì":
                                            classroom_info = "Zoom (mercoledì)"
                                            classroom_url  = "https://uniroma1.zoom.us/j/81579067494?pwd=D1gMJxvBKdpVKIKQJtK6abN4yBxVza.1"
                                    # PROGETTAZIONE DI SISTEMI DIGITALI - 1015880 - Salvatore Pontarelli
                                    elif (course_code == "1015880") and (channel_id == "1"):
                                        classroom_info = "Zoom (link ancora da annunciare)"
                                    # ALGEBRA - 1015886 - Viaggi e Cherubini
                                    elif (course_code == "1015886") and (channel_id == "1"):
                                        classroom_info = "Meet"
                                        classroom_url  = "https://meet.google.com/wwi-vnmh-nof"
                                    # CALCOLO DELLE PROBABILITA' - 1020421 - Giovanna Nappo
                                    elif (course_code == "1020421") and (channel_id == "1"):
                                        classroom_info = "Meet"
                                        classroom_url  = "https://meet.google.com/saf-hhcd-odh"
                                    # SISTEMI OPERATIVI - 1020422 - Gabriele Tolomei
                                    elif ("1020422" in course_code) and (channel_id == "1"):
                                        classroom_info = zoom_register_it
                                        classroom_url  = "https://uniroma1.zoom.us/meeting/register/tZMpceiqqT4iH9UBeCqtHlU6JThiuv5qYbBR"
                                    # BASI DI DATI - 1015887 - Giuseppe Perelli
                                    elif ("1015887" in course_code) and (channel_id == "1"):
                                        classroom_info = zoom_login_it
                                        classroom_url  = "https://uniroma1.zoom.us/j/84021213956"
                                    # ALGEBRA - 1015886 - Federico Pellarin
                                    elif (course_code == "1015886") and (channel_id == "2"):
                                        if day_name in ("martedì", "mercoledì"):
                                            classroom_info = "Meet"
                                            classroom_url  = "https://meet.google.com/jcm-mnfz-nqn"
                                    # CALCOLO DELLE PROBABILITÀ - 1020421 - Alessandra Faggionato
                                    elif (course_code == "1020421") and (channel_id == "2"):
                                        classroom_info = "Zoom"
                                        classroom_url  = "https://uniroma1.zoom.us/j/81062850219"
                                    # BASI DI DATI - 1015887 - Maria De Marsico
                                    elif ("1015887" in course_code) and (channel_id == "2"):
                                        if day_name == "mercoledì":
                                            classroom_info = zoom_register_it
                                            classroom_url  = "https://uniroma1.zoom.us/meeting/register/tZAqde6urDojEtXQAyiwJGAgdSKGHol6-f-L"
                                    # AUTOMI CALCOLABILITA' E COMPLESSITA' - 1041727 - Daniele Venturi
                                    elif course_code == "1041727":
                                        if day_name == "venerdì":
                                            classroom_info = "Zoom"
                                            classroom_url  = "https://uniroma1.zoom.us/j/86123921107?pwd=YICFZ9rvjNF2eSqU7mN6c8xoJOIndS.1"


                                    # ACSAI


                                    # CALCULUS - 10595099 - Adriano Pisante
                                    elif "10595099" in course_code:
                                        classroom_info = zoom_register_en
                                        classroom_url  = "https://uniroma1.zoom.us/meeting/register/tZ0lcu6vrjoqH9F0Pr8RvGa-TMrruVjvlC7g"

                                    # COMPUTER ARCHITECTURE - 10595546 - Daniele De Sensi
                                    elif "10595546" in course_code:
                                        classroom_info = "Zoom"
                                        classroom_url  = "https://uniroma1.zoom.us/my/desensi"

                                    # LINEAR ALGEBRA - 10595524 - Sahar Zabad
                                    elif course_code == "10595524":
                                        if day_name == "lunedì":
                                            classroom_info = "Zoom (monday)"
                                            classroom_url = "https://us04web.zoom.us/j/73625581520?pwd=16l3Pq9cVjQQizkiYMzIkgBbOPivlO.1"
                                        elif day_name == "venerdì":
                                            classroom_info = "Zoom (friday)"
                                            classroom_url = "https://us04web.zoom.us/j/73508542218?pwd=GM0Z8b8LEEBLn5cu2DtilP5mUFyIYR.1"

                                    # PROGRAMMING UNIT 1 - 10595102 - Maurizio Mancini
                                    elif course_code == "10595102_1":
                                        classroom_info = "Zoom"
                                        classroom_url = "https://uniroma1.zoom.us/j/83935295835?pwd=dfrv1RYMIb4svV41mCTKJ3WNDaX98y.1"

                                    # CALCULUS 2 - 10595529 - Alessandro Alla
                                    elif course_code == "10595529":
                                        classroom_info = "Zoom"
                                        classroom_url  = "https://uniroma1.zoom.us/j/87650619184?pwd=p3CJTHaBga47OFuLtze6A4Y8GCfPbq.1"

                                    # DATA MANAGEMENT AND ANALYSIS - 10595617 - Giuseppe Perelli
                                    elif course_code == "10595617_1":
                                        classroom_info = zoom_login_en
                                        classroom_url  = "https://uniroma1.zoom.us/j/87151615100"

                                    # PROBABILITY - 10595525 - Lorenzo Bertini Malgarini, Vittoria Silvestri
                                    elif course_code == "10595525":
                                        if day_name == "lunedì":
                                            classroom_info = "Zoom"
                                            classroom_url = "https://uniroma1.zoom.us/j/8842067418?pwd=SFRjdVNheStLbGZMeWdyUWJrSFc0Zz09"

                                    # SYSTEMS AND NETWORKING unit 1 - 10595616 - Gabriele Tolomei
                                    elif course_code == "10595616_1":
                                        classroom_info = zoom_register_en
                                        classroom_url  = "https://uniroma1.zoom.us/meeting/register/tZYtduuvrTkiGNxQ_0FUu0ggIflseYCOzafM"

                                    # SYSTEMS AND NETWORKING unit 2 - 10595616 - Novella Bartolini
                                    elif course_code == "10595616_2":
                                        classroom_info = "Zoom"
                                        classroom_url  = "https://uniroma1.zoom.us/j/81664845095?pwd=WAxUSVRBjt09P3RsuUDna3MmheqG65.1"

                                # PROGRAMMAZIONE PER IL WEB - 1022267 - Emanuele Panizzi
                                # WEB AND SOFTWARE ARCHITECTURE - 10595534 - Emanuele Panizzi
                                if course_code in ("1022267", "10595534"):
                                    if day_name == "giovedì":
                                        classroom_info = reginaelena_edificiod_301
                                        classroom_url  = reginaelena_edificiod
                                # DEEP LEARNING - 10595531 - Luigi Cinque, Fabio Galasso
                                elif course_code == "10595531":
                                    if day_name == "lunedì":
                                        classroom_info = scienzebiochimiche_aulab
                                        classroom_url  = scienzebiochimiche_building
                                    elif day_name == "giovedì":
                                        classroom_info = reginaelena_edificiod_301
                                        classroom_url  = reginaelena_edificiod

                                if classroom_info is not None:
                                    day_schedule.pop("classrooms")

                                    print("classroom_info: " + classroom_description + " -> " + classroom_info)

                                    day_schedule["classroomInfo"] = classroom_info
                                else:
                                    print("classroom_info: " + classroom_description)

                                if classroom_url is not None:
                                    day_schedule["classroomUrl"] = classroom_url

    #
    # ▒█▀▀▀ ▀▄▒▄▀ ▒█▀▀█ ▒█▀▀▀█ ▒█▀▀█ ▀▀█▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
    # ▒█▀▀▀ ░▒█░░ ▒█▄▄█ ▒█░░▒█ ▒█▄▄▀ ░▒█░░ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
    # ▒█▄▄▄ ▄▀▒▀▄ ▒█░░░ ▒█▄▄▄█ ▒█░▒█ ░▒█░░ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
    #

    # Save the classroom information to a JSON file
    with open(f"../data/classrooms.json", 'w') as classroomsFile:
        json.dump(escape_dict_double_quotes(classrooms_dict), classroomsFile, indent=2)

    # Save the teacher information to a JSON file
    with open(f"../data/teachers.json", 'w') as teachersFile:
        json.dump(escape_dict_double_quotes(teachers_dict), teachersFile, indent=2)

    # Save the course timetables to a JSON file
    with open(f"../data/timetables.json", 'w') as timetablesFile:
        json.dump(escape_dict_double_quotes(course_timetables_dict), timetablesFile, indent=2)
