# парсим erc-20 rate на etherscan

from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from datetime import datetime
import re
import csv

ERC_20_RATE = 'https://etherscan.io/tokens?p='
PAGES = 19

def get_html(url):
    ua = UserAgent().random
    r = requests.get(url, stream=True, headers = {'User-Agent': ua})

    return r.text

def get_token_names(page_numb):
    url = ERC_20_RATE + str(page_numb)
    soup = BeautifulSoup(get_html(url), 'lxml')
    h3s = soup.find_all('h3', class_='h6')
    names = []
    for h in h3s:
        name = h.text
        name = re.sub(r'\([^()]*\)', '', name)
        names.append(name)

    return names


def main():
    start = datetime.now()

    names = []
    for p in range(1, PAGES+1):
        names_on_page = get_token_names(p)
        names.extend(names_on_page)

    with open('erc-20.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['erc20_name'])
        for name in names:
            csv_writer.writerow([name])

    print(f'Спарсено за {datetime.now()-start}')


if __name__ == '__main__':
    main()
