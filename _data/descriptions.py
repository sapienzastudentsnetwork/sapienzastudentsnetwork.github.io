from scraper import scrape


def parse(data, DOM):
    data = {}

    for element in DOM.find_all('tr', class_='insegnamento'):
        try:
            course = element.find(class_='insegnamento-title').text.split()[0]
            data[course] = element.find(attrs={'style': 'display:none;'}).text
        except Exception:
            pass

    return data


scrape(
    'https://corsidilaurea.uniroma1.it/it/corso/2023/29923/cds',
    'file.json',
    parse,
    target='descriptions.json',
    lint=lambda content: ' '.join(content.decode('utf-8').split(' ')),
)
