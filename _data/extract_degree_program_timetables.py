import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
display = Display(visible=0, size=(1920, 1080))
display.start()

import re

import json

#
# ▒█▀▀▀█ ▒█▀▀█ ▒█▀▀█ ░█▀▀█ ▒█▀▀█ ▒█▀▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
# ░▀▀▀▄▄ ▒█░░░ ▒█▄▄▀ ▒█▄▄█ ▒█▄▄█ ▒█▀▀▀ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
# ▒█▄▄▄█ ▒█▄▄█ ▒█░▒█ ▒█░▒█ ▒█░░░ ▒█▄▄▄ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
#

# Semester to scrape timetables and classrooms for
semester = os.getenv("SEMESTER")

# Degree program to scrape timetables and classrooms for
degreeProgramCode = os.getenv("DEGREEPROGRAMCODE", "")

# Url of the university page containing timetables and classrooms for the specific degree program
url = os.getenv("ORARI_BASE_URL") + f"/{degreeProgramCode}"

# Suffix for the output timetables file name
# - timetables{suffix}.json - including all timetables in the page

suffix = os.getenv("SUFFIX", "")

# Initialize the Firefox browser driver
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Get the HTML source code of the webpage
driver.get(url)
html = driver.page_source

# Parse the HTML code using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all 'table' elements on the page
table_elements = soup.find_all('table')

# Since there is a h3 element for each schedule table, counting
# the h3 elements allows us to count the number of timetables
number_of_timetables = len(soup.find_all('h3'))

# Find all 'h2' elements on the page; These will be associated with 'h3' elements
h2_tags = soup.find_all('h2')

# Having completed the scraping part, we can quit the driver
driver.quit()

#
# ▒█░░░ ▒█▀▀▀█ ░█▀▀█ ▒█▀▀▄ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
# ▒█░░░ ▒█░░▒█ ▒█▄▄█ ▒█░▒█ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
# ▒█▄▄█ ▒█▄▄▄█ ▒█░▒█ ▒█▄▄▀ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
#


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


# Dictionary to store classroom information
classrooms_file_name = "classrooms.json"
classrooms_dict = load_dict_from_json(classrooms_file_name)

# Dictionary to store teacher info
teachers_file_name = "teachers.json"
teachers_dict = load_dict_from_json(teachers_file_name)

# Dictionary to store teaching schedules
teaching_schedules_file_name = "schedules.json"
teaching_schedules_dict = load_dict_from_json(teaching_schedules_file_name)


#
# ▒█▀▀▀ ▀▄▒▄▀ ▀▀█▀▀ ▒█▀▀█ ░█▀▀█ ▒█▀▀█ ▀▀█▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
# ▒█▀▀▀ ░▒█░░ ░▒█░░ ▒█▄▄▀ ▒█▄▄█ ▒█░░░ ░▒█░░ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
# ▒█▄▄▄ ▄▀▒▀▄ ░▒█░░ ▒█░▒█ ▒█░▒█ ▒█▄▄█ ░▒█░░ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
#

# For the file 'timetables.json', we want a structure like this:
# {
#   "<year_id>": {
#     "<channel_id>": {
#       "timetable": {
#         "monday": {
#           ...
#         },
#         ...
#         "friday": {
#           ...
#         }
#       }
#       "title": "<description of the timetable (e.g. 'Primo Anno A-L')>"
#     },
#     ...
#   },
#   ...
# }

# In the page structure, there is a h2 element for each year,
# and "within it" a h3 element for each channel

# The h2 elements contain text in this format:
# <Primo/secondo/terzo/...> anno - <primo/secondo> semestre

# The h3 elements contain text in this format:
# Canale <Unico/1/2/...>

# We will use the ID of the channels taken from the h3 elements,
# using '0' (because we want it this way) as the ID to represent
# the special case of the Single Channel ("Canale Unico")

# We will use an incremental counter as the year's ID instead

year_and_channel_indexes = []

count = 0

table_index = 0

for h2_tag in h2_tags:
    h2_tag_text = h2_tag.text

    h3_tags = h2_tag.find_next_siblings('h3')

    h3_texts = [
        h3.text.split()[-1] if h3.text.split()[-1] != "Unico" else '0' for h3 in h3_tags
    ]

    if "semestre" not in h2_tag_text or f"{semester} semestre" in h2_tag_text:
        for h3_text in h3_texts:
            year_and_channel_indexes.append((str(count), str(h3_text)))

            table_index += 1

        count += 1

    else:
        for h3_text in h3_texts:
            del table_elements[table_index]

            number_of_timetables -= 1

# Dictionary to store class timetables
timetables_dict = {}


# Function to translate Italian day names to English
def translate_day_name(italian_day_name) -> str:
    days_translation = {
        "lunedì": "monday",
        "martedì": "tuesday",
        "mercoledì": "wednesday",
        "giovedì": "thursday",
        "venerdì": "friday"
    }

    return days_translation.get(italian_day_name, None)


# Iterate through the tables and extract class timetables
for table_index, table in enumerate(table_elements):
    # The following table will be the one for classrooms,
    # which we clearly shouldn't interpret in the same way
    # as the tables containing the class schedules
    if (table_index + 1) > number_of_timetables:
        break

    # Extract year index and channel for the current timetable
    year_index, channel = year_and_channel_indexes[table_index]

    if year_index not in timetables_dict:
        timetables_dict[year_index] = {}

    # Find all table rows, excluding the first row with headers
    rows = table.find_all('tr')[1:]

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

    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 3:
            # Find the <a> element containing the teaching's code
            teaching_code_link = columns[0].find('a')

            # Extract the teaching code from the link
            teachingCode = teaching_code_link.get_text(strip=False).split(" ")[0]

            # Extract class timings from the third column
            day_and_time_strings = str(columns[2]).replace("dalle ", "").replace("alle ", "").replace(":00", "")

            if channel not in timetables_dict[year_index]:
                timetables_dict[year_index][channel] = {
                    "timetable": {
                        "monday": [],
                        "tuesday": [],
                        "wednesday": [],
                        "thursday": [],
                        "friday": []
                    }
                }

            for day_and_time_string in day_and_time_strings.replace("<td> ", "").replace("</td>", "").split("<br/>"):
                # e.g. lunedì dalle 08:00 alle 11:00
                day_and_time_string_fields = day_and_time_string.split(" ")

                day_name  = translate_day_name(day_and_time_string_fields[0])
                startTime = day_and_time_string_fields[1]
                endTime   = day_and_time_string_fields[2]

                # Add the class schedule to the timetables dictionary
                timetables_dict[year_index][channel]["timetable"][day_name].append({
                    "startTime": int(startTime),
                    "endTime": int(endTime),
                    "code": teachingCode
                })

                teacherName    = None
                teacherPageUrl = None

                # Find the <a> element containing the teacher's name
                teacher_div = columns[0].find('div', class_='docente')

                if teacher_div:
                    teacher_a = teacher_div.find('a')

                    # Extract the teacher's name
                    teacherName = teacher_a.text

                    # Extract the URL of the teacher's page
                    teacherPageUrl = teacher_a['href']

                    # Extract the teacher's UID from the URL of the teacher's page
                    teacherId = teacherPageUrl.split('=')[-1]

                    if teacherId not in teachers_dict:
                        teachers_dict[teacherId] = {
                            "teacherName": teacherName,
                            "teacherPageUrl": teacherPageUrl
                        }
                    else:
                        teachers_dict[teacherId]["teacherName"] = teacherName
                        teachers_dict[teacherId]["teacherPageUrl"] = teacherPageUrl
                else:
                    teacherId = None

                # Extract location information from column 1 of the table
                location = columns[1]

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
                classroomId = columns[1].find('a').get('href').replace("#aula_", "")

                
                if teachingCode not in teaching_schedules_dict:
                    teaching_schedules_dict[teachingCode] = {
                        "degree": degreeProgramCode,
                        "channels": {}
                    }

                if f"{channel}" not in teaching_schedules_dict[teachingCode]["channels"]:
                    teaching_schedules_dict[teachingCode]["channels"][f"{channel}"] = {}

                if day_name not in teaching_schedules_dict[teachingCode]["channels"][f"{channel}"]:
                    # Create a new dictionary for the day name with class information for the channel
                    teaching_schedules_dict[teachingCode]["channels"][f"{channel}"][day_name] = {
                        "teacherId": teacherId,
                        "hours": f"{startTime} - {endTime}",
                        "classrooms": {
                            classroomId: location
                        }
                    }
                else:
                    # If the day name is already present, add the location to the list of classrooms
                    #
                    # Useful for teachings that are held in more than one
                    # classroom at the same time (usually those in laboratories)
                    #

                    teaching_schedules_dict[teachingCode]["channels"][f"{channel}"][day_name]["classrooms"][classroomId] = location
                teaching_schedules_dict[teachingCode]["code"] = teachingCode

    # Remove duplicates and sort class timetables
    for day, classes in timetables_dict[year_index][channel]["timetable"].items():
        unique_classes = {}
        for cls in classes:
            unique_key = (cls["startTime"], cls["endTime"], cls["code"])
            unique_classes[unique_key] = cls
        
        unique_classes = list(unique_classes.values())
        
        timetables_dict[year_index][channel]["timetable"][day] = sorted(unique_classes, key=lambda x: x["startTime"])

sort_days_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]

# Hard-code the alignment of ACSAI "Optimization"'s class schedules with those of "Modelli e Ottimizzazione" for the A.Y. 2023-2024
if "1022265" in teaching_schedules_dict and "10595533" not in teaching_schedules_dict:
    teaching_schedules_dict["10595533"] = teaching_schedules_dict["1022265"]

# Hard-code the alignment of Basi di Dati II's Channel 2 class schedules with those of Channel 1 for the A.Y. 2023-2024
if "1015887" in teaching_schedules_dict and "2" not in teaching_schedules_dict["1015887"]["channels"]:
    teaching_schedules_dict["1015887"]["channels"]["2"] = teaching_schedules_dict["1015887"]["channels"]["1"]

# Refine "teaching_schedules_dict" dictionary
for teaching_code, teaching_code_data in teaching_schedules_dict.items():
    sorted_channels = {}

    for channel, day_data in teaching_code_data["channels"].items():
        sorted_days = {day: day_data[day] for day in sort_days_order if day in day_data}
        sorted_channels[channel] = sorted_days

    teaching_schedules_dict[teaching_code]["channels"] = sorted_channels

# Refine "timetables_dict" dictionary
if "29923" in url:
    if '0' in timetables_dict and '1' in timetables_dict['0']:
        timetables_dict['0']['1']["title"] = "Primo Anno A-L"
    if '0' in timetables_dict and '2' in timetables_dict['0']:
        timetables_dict['0']['2']["title"] = "Primo Anno M-Z"
    if '1' in timetables_dict and '1' in timetables_dict['1']:
        timetables_dict['1']['1']["title"] = "Secondo Anno A-L"
    if '1' in timetables_dict and '2' in timetables_dict['1']:
        timetables_dict['1']['2']["title"] = "Secondo Anno M-Z"
    if '2' in timetables_dict and '0' in timetables_dict['2']:
        timetables_dict['2']['0']["title"] = "Terzo Anno"

if "30786" in url:
    if '0' in timetables_dict and '0' in timetables_dict['0']:
        timetables_dict['0']['0']["title"] = "Primo Anno"

    if '1' in timetables_dict and '0' in timetables_dict['1']:
        timetables_dict['1']['0']["title"] = "Secondo Anno"

    if '2' in timetables_dict and '0' in timetables_dict['2']:
        timetables_dict['2']['0']["title"] = "Terzo Anno"

# In the page structure, it is planned that after the tables
# containing the schedules, there is a single table with more
# information about the classrooms indicated in the schedules

# Find all the rows in the table except the first one (header)
rows = table_elements[table_index].find_all('tr')[1:]

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

        address = td_tags[1].text.strip().split("  ROMA  ")[0]
        if "presso" in address:
            address = None

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


# Save the classroom information to a JSON file
with open(f"classrooms.json", "w") as classroomsFile:
    json.dump(escape_dict_double_quotes(classrooms_dict), classroomsFile, indent=2)

# Save the teacher information to a JSON file
with open(f"teachers.json", "w") as teachersFile:
    json.dump(escape_dict_double_quotes(teachers_dict), teachersFile, indent=2)

# Save the teaching schedules to a JSON file
with open(f"schedules.json", "w") as schedulesFile:
    json.dump(escape_dict_double_quotes(teaching_schedules_dict), schedulesFile, indent=2)

# Save the class timetables to a JSON file
#with open(f"timetables{suffix}.json", "w") as timetablesFile:
#    json.dump(escape_dict_double_quotes(timetables_dict), timetablesFile, indent=2)
