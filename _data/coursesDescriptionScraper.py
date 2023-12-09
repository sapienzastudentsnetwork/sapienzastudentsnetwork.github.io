import requests
from bs4 import BeautifulSoup
import json


#Parser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
page = requests.get('https://corsidilaurea.uniroma1.it/it/corso/2021/29923/cds', headers=headers)
soup = BeautifulSoup(page.content.decode('utf-8'), 'html.parser')



courseText = soup.find_all("div", attrs={'style':'display:none;'}) # => Course without the associated id
courseDescription = {} # => {'id':'text'}
invalidIds = soup.find_all("td", class_="open-insegnamento-detail insegnamento-title") #Not filtered invalidIds
ids = list() # Filtered invalidIds
#Ids' filter
for i in invalidIds:
    a = i.text
    if "-" in a and a.split(" ")[4]!="":
        ids.append(a.split(" ")[4])
    
#put data in courseDescription
for x, i in enumerate(courseText):
    c = ""
    for l in i:
        c+=l.text
        c+="\n"
    courseDescription[ids[x]] = c

#save everything in json
with open('coursesDescription.json', 'w') as fp:
    json.dump(courseDescription, fp, indent=2)
