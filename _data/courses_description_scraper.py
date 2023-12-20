from scraper import scrape


def parse(data, DOM):
    data = {}

    for element in DOM.find_all('tr', class_='insegnamento'):
        try:
            course = element.find(class_='insegnamento-title').text.split()[0]
            data[course] = element.find(attrs={'style': 'display:none;'}).text
        except Exception:
            print(element)

    return data


scrape(
    'https://corsidilaurea.uniroma1.it/it/corso/2023/29923/cds',
    'file.json',
    parse,
    target='descriptions.json',
    lint=lambda content: ' '.join(content.decode('utf-8').split(' ')),
)

# import requests
# from requests import get
# import json
# from bs4 import BeautifulSoup
# Parser
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
# }

# 'https://corsidilaurea.uniroma1.it/it/corso/2021/29923/cds',
#
# page = get(
#     'https://corsidilaurea.uniroma1.it/it/corso/2021/29923/cds',
#     headers={
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
#         'Content-Type': 'text/html'
#     }
# )

# soup = BeautifulSoup(page.content.decode('unicode-escape'), 'html.parser')

# # => Course without the associated id
# course_text = soup.find_all("div", attrs={'style': 'display:none;'})
# course_description = {}  # => {'id':'text'}
#
# invalid_ids = soup.find_all(
#     "td", class_="open-insegnamento-detail insegnamento-title")  # Not filtered invalidIds
# ids = list()  # Filtered invalidIds
#
# # Ids' filter
# for invalid_id in invalid_ids:
#     if "-" in invalid_id.text and invalid_id.text.split(" ")[4] != "":
#         ids.append(invalid_id.text.split(" ")[4])
#
# # put data in course_description
# for course_index, description in enumerate(course_text):
#     course_description[ids[course_index]] = ""
#     for paragraph in description:
#         course_description[ids[course_index]] += paragraph.text + "<br/>"
#
# # save everything in json
# with open('coursesDescription.json', 'w') as fp:
#     json.dump(course_description, fp, indent=2)
