import requests
from bs4 import BeautifulSoup
import json


# Parser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
page = requests.get(
    'https://corsidilaurea.uniroma1.it/it/corso/2021/29923/cds', headers=headers)
soup = BeautifulSoup(page.content.decode('utf-8'), 'html.parser')


# => Course without the associated id
course_text = soup.find_all("div", attrs={'style': 'display:none;'})
course_description = {}  # => {'id':'text'}

invalid_ids = soup.find_all(
    "td", class_="open-insegnamento-detail insegnamento-title")  # Not filtered invalidIds
ids = list()  # Filtered invalidIds

# Ids' filter
for invalid_id in invalid_ids:
    if "-" in invalid_id.text and invalid_id.text.split(" ")[4] != "":
        ids.append(invalid_id.text.split(" ")[4])

# put data in course_description
for course_index, description in enumerate(course_text):
    course_description[ids[course_index]] = ""
    for paragraph in description:
        course_description[ids[course_index]] += paragraph.text + "<br/>"

# save everything in json
with open('../data/coursesDescription.json', 'w') as fp:
    json.dump(course_description, fp, indent=2)
