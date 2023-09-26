import os

from selenium import webdriver
from bs4 import BeautifulSoup

import re

import json

#
# ▒█▀▀▀█ ▒█▀▀█ ▒█▀▀█ ░█▀▀█ ▒█▀▀█ ▒█▀▀▀ 　 ▒█▀▀▄ ░█▀▀█ ▀▀█▀▀ ░█▀▀█
# ░▀▀▀▄▄ ▒█░░░ ▒█▄▄▀ ▒█▄▄█ ▒█▄▄█ ▒█▀▀▀ 　 ▒█░▒█ ▒█▄▄█ ░▒█░░ ▒█▄▄█
# ▒█▄▄▄█ ▒█▄▄█ ▒█░▒█ ▒█░▒█ ▒█░░░ ▒█▄▄▄ 　 ▒█▄▄▀ ▒█░▒█ ░▒█░░ ▒█░▒█
#

# Url of the university page containing timetables and classrooms for a specific degree program
url = os.getenv("URL", "")

# Suffix for the output file names
# - classrooms{suffix}.json - including classrooms data
# - schedules{suffix}.json - including schedules data for each subject
# - timetables{suffix}.json - including all timetables in the page

suffix = os.getenv("SUFFIX", "")

# Initialize the Firefox browser driver
driver = webdriver.Firefox()

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

for h2_tag in h2_tags:
    h3_tags = h2_tag.find_next_siblings('h3')

    h3_texts = [
        h3.text.split()[-1] if h3.text.split()[-1] != "Unico" else '0' for h3 in h3_tags
    ]

    for h3_text in h3_texts:
        year_and_channel_indexes.append((str(count), str(h3_text)))

    count += 1

# Dictionary to store class timetables
timetables = {}

# Dictionary to store teaching schedules
teaching_schedules_dict = {}


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

    if year_index not in timetables:
        timetables[year_index] = {}

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

            if channel not in timetables[year_index]:
                timetables[year_index][channel] = {
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
                timetables[year_index][channel]["timetable"][day_name].append({
                    "startTime": int(startTime),
                    "endTime": int(endTime),
                    "code": int(teachingCode)
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
                    teaching_schedules_dict[teachingCode] = {}

                if f"{channel}" not in teaching_schedules_dict[teachingCode]:
                    teaching_schedules_dict[teachingCode][f"{channel}"] = {}

                if day_name not in teaching_schedules_dict[teachingCode][f"{channel}"]:
                    # Create a new dictionary for the day name with class information for the channel
                    teaching_schedules_dict[teachingCode][f"{channel}"][day_name] = {
                        "teacherName": teacherName,
                        "teacherPageUrl": teacherPageUrl,
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

                    teaching_schedules_dict[teachingCode][f"{channel}"][day_name]["classrooms"][classroomId] = location

    # Remove duplicates and sort class timetables
    for day, classes in timetables[year_index][channel]["timetable"].items():
        unique_classes = {}
        for cls in classes:
            unique_key = (cls["startTime"], cls["endTime"], cls["code"])
            unique_classes[unique_key] = cls
        
        unique_classes = list(unique_classes.values())
        
        timetables[year_index][channel]["timetable"][day] = sorted(unique_classes, key=lambda x: x["startTime"])

sort_days_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]

# Refine "teaching_schedules_dict" dictionary
sorted_schedules = {}

for teaching_code, channel_data in teaching_schedules_dict.items():
    sorted_channels = {}

    for channel, day_data in channel_data.items():
        sorted_days = {day: day_data[day] for day in sort_days_order if day in day_data}
        sorted_channels[channel] = sorted_days

    sorted_schedules[teaching_code] = sorted_channels

# Refine "timetables" dictionary
if "29923" in url:
    if '0' in timetables and '1' in timetables['0']:
        timetables['0']['1']["title"] = "Primo Anno A-F"
    if '0' in timetables and '2' in timetables['0']:
        timetables['0']['2']["title"] = "Primo Anno G-Z"
    if '1' in timetables and '1' in timetables['1']:
        timetables['1']['1']["title"] = "Secondo Anno A-L"
    if '1' in timetables and '2' in timetables['1']:
        timetables['1']['2']["title"] = "Secondo Anno M-Z"
    if '2' in timetables and '0' in timetables['2']:
        timetables['2']['0']["title"] = "Terzo Anno"

if "30786" in url:
    if '0' in timetables and '0' in timetables['0']:
        timetables['0']['0']["title"] = "Primo Anno"

    if '1' in timetables and '0' in timetables['1']:
        timetables['1']['0']["title"] = "Secondo Anno"

    if '2' in timetables and '0' in timetables['2']:
        timetables['2']['0']["title"] = "Terzo Anno"

# Dictionary to store classroom information
classrooms = {}

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
        classrooms[id] = {
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
    input_dict_json_string = json.dumps(input_dict)
    
    # Return dict with double quote characters within the JSON string replaced with escaped double quotes
    return json.loads(input_dict_json_string.replace('\\"', '\\\\\\"'))


# Save the classroom information to a JSON file
with open(f"classrooms{suffix}.json", "w") as classroomsFile:
    json.dump(escape_dict_double_quotes(classrooms), classroomsFile, indent=2)

# Save the teaching schedules to a JSON file
with open(f"schedules{suffix}.json", "w") as schedulesFile:
    json.dump(escape_dict_double_quotes(sorted_schedules), schedulesFile, indent=2)

# Save the class timetables to a JSON file
with open(f"timetables{suffix}.json", "w") as timetablesFile:
    json.dump(escape_dict_double_quotes(timetables), timetablesFile, indent=2)
