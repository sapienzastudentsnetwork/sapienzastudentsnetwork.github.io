from scraper import scrape


def parse(data, DOM):
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
                    'subject': teaching.find('a').text,
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

    print(data)
    return data


# ignore
scrape(
    'https://gomppublic.uniroma1.it/ScriptService/OffertaFormativa/Ofs.6.0/AuleOrariScriptService/GenerateOrario.aspx?params={"controlID":"","aulaUrl":"","codiceInterno":29923,"annoAccademico":"2023/2024","virtuale":false,"timeSlots":null,"displayMode":"Manifesto","showStyles":true,"codiceAulaTagName":"","nomeAulaCssClass":"","navigateUrlInsegnamentoMode":"","navigateUrlInsegnamento":"","navigateUrlDocenteMode":"","navigateUrlDocente":"","repeatTrClass":""}&_=1702740827520',
    'schedules.json',
    parse,
    target='test.json',
    lint=lambda content: ' '.join(
        content[13:-3].decode('unicode-escape').split()),
)
