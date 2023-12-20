from requests import get
from datetime import datetime
from json import dump, load, JSONDecodeError
from bs4 import BeautifulSoup
from os import path, rename


def lint(content):
    return ' '.join(content.split())


def scrape(url, source, parse, target=None, lint=lint):
    DOM = BeautifulSoup(
        lint(get(url).content),
        'html.parser'
    )

    with open(target if target else source, 'w') as file:
        dump(parse(load_dict(source), DOM), file, indent=2)


def load_dict(source):
    if path.exists(source):
        try:
            # Try to open the file as JSON
            with open(source, 'r') as file:
                data = load(file)

                print(
                    f"File '{source}' opened successfully and loaded as a dictionary.")

                return data

        except JSONDecodeError:
            # If the file is not a valid JSON, rename the file by adding the .bak extension
            # with the current date and time to avoid overwriting it when it might not be desired
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup = f"{source}.bak{now}"
            rename(source, backup)

            print(f"The file '{
                  source}' is not a valid JSON, renamed to '{backup}'.")
    else:
        print(f"File '{source}' not found.")

    return {}
