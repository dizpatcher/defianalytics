from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import csv
from datetime import datetime

BIT_QUERY_API_KEY = ''
ES_ADDR_URL = 'https://etherscan.io/address/'


txns = ['0xade227c3ad59395cf7a15ceb56085a77c61a29216858fc789d8413ef929a5fbe',
        '0x4494df0f8db3a839ed914bfa58103f7e01b85d159a7d7d6c1851044aa35eadcb',
        '0x8c8c579b81e40d412c969951c36c8b60a650d626a080bdcf812e0e82b4e72535',
        '0x36682e448066ae1831d216c8c4cb3432c7cdddd17c5cd2f17e6582320af68e0b',
        '0x1d7ed2a71554e69289f7e6602d9f9ef2b9171489966fea336ba9c6670f0fc0e5',
        '0xbfdbbfd8d016f960858bf505b5dccd614f5066aef91b5cb756b7f12f8b7fc532',
        '0x9bc514d784ee389511d16ad66a47dc9b58e7a7717efec5609e61f6bf1539717c',
        '0x2e75b9222616e3970d5408fe33ab994f02f3a207af4dd003fa7ea4b94fbaddbd',
        '0x88e486e56b68fa127b93e9c394f5a91e2304c70f7f800acfbe88703f8456b601']


def run_query(query):
    headers = {'X-API-KEY': BIT_QUERY_API_KEY}
    request = requests.post('https://graphql.bitquery.io/',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f'Ошибка с кодом {request.status_code}:\n {query}')


def get_contracts_for_txn(txn):

    query = f"""
    query{{
      ethereum(network: ethereum) {{
        smartContractCalls(
          options: {{asc: "callDepth"}}
          txHash: {{ is: "{txn}" }}
        ) {{
          smartContract {{
            address {{
              address
              annotation
            }}
            contractType
            protocolType
            currency {{
              symbol
            }}
          }}
          smartContractMethod {{
            name
            signatureHash
          }}
          caller {{
            address
            annotation
            smartContract {{
              contractType
              currency {{
                symbol
            }}
          }}
          }}
          success
          amount
          gasValue
          callDepth
        }}
      }}
    }}
    """

    txn_data  = run_query(query)
    contractCalls = txn_data['data']['ethereum']['smartContractCalls']
    addresses = []
    for cc in contractCalls:
        contract = cc['smartContract']['address']['address']
        addresses.append(contract)

    addresses = list(set(addresses))

    return {'txn': txn,
            'contracts': addresses}


def get_html(url):
    ua = UserAgent().random
    r = requests.get(url, stream=True, headers = {'User-Agent': ua})

    return r.text


def get_public_tag_name(txn_numb, txn, contract):
    url = ES_ADDR_URL + contract

    soup = BeautifulSoup(get_html(url), 'lxml')
    header = soup.find('div', class_="card-header")
    #data-original-title="Public Name Tag (viewable by anyone)"

    try:
        tag = header.span.text
        link = header.a.get('href')
    except AttributeError as e:
        tag = ''
        link = ''

    contract = {
                'numb': txn_numb,
                'txn': txn,
                'url': url,
                'tag': tag,
                'tag_link': link
                }

    return contract



def main():

    start = datetime.now()

    df = []
    txn_contracts = []
    for txn in txns:
        txn_contracts.append(get_contracts_for_txn(txn))

    for i, tc in enumerate(txn_contracts):
        for contract in tc['contracts']:
            contract_data = get_public_tag_name(i+1, tc['txn'], contract)
            print(f'Получен контракт {ES_ADDR_URL+contract} транзакции {i+1}')
            df.append(contract_data)

    with open('public_tags.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(df[0].keys())

        for contract_data in df:
            csv_writer.writerow(contract_data.values())

    finish = datetime.now()
    print(f'Спарсено за {finish-start}')


if __name__ == '__main__':
    main()
