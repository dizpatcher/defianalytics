import requests
import csv
from datetime import datetime

BIT_QUERY_API_KEY = ''
ES_ADDR_URL = 'https://etherscan.io/address/'
DATAFRAME = 'public_tags.csv'

def run_query(query):
    headers = {'X-API-KEY': BIT_QUERY_API_KEY}
    request = requests.post('https://graphql.bitquery.io/',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f'Ошибка с кодом {request.status_code}:\n {query}')


def get_contract_info(txn_numb, txn, addr):

    query = f"""
    query{{
      ethereum(network: ethereum) {{
        smartContractCalls(
          smartContractAddress: {{is: "{addr}"}}
          smartContractType: {{}}
          txFrom: {{}}
        ) {{
          smartContract {{
            address {{
              address
              annotation
            }}
            contractType
            currency {{
              name
              tokenType
            }}
          }}
          smartContractMethod {{
            name
            signature
            signatureHash
          }}
        }}
      }}
    }}
    """

    contract_details = run_query(query)['data']['ethereum']['smartContractCalls']
    need_info = {
            'numb': txn_numb,
            'txn': txn,
            'address': ES_ADDR_URL + addr,
            'annotations': [],
            'currencies': [],
            'types': [],
            'methods': []
    }

    annotations, types, currencies, methods = [], [], [], []
    for det in contract_details:
        annt = det['smartContract']['address']['annotation']
        if annt:
            annotations.append(annt)

        type = det['smartContract']['contractType']
        if type:
            types.append(type)

        cur = det['smartContract']['currency']['name']
        if cur:
            currencies.append(cur)

        method = det['smartContractMethod']['name']
        if method:
            methods.append(method)


    need_info['annotations'] = ', '.join(list(set(annotations)))
    need_info['types'] = ', '.join(list(set(types)))
    need_info['currencies'] = ', '.join(list(set(currencies)))
    need_info['methods'] = ', '.join(list(set(methods)))

    return need_info



def main():

    start = datetime.now()

    data = []
    with open(DATAFRAME, 'r') as df:
        contracts = csv.DictReader(df, delimiter=',')

        for contract in contracts:
            data.append(get_contract_info(contract['numb'],
                                          contract['txn'],
                                          contract['url'].split('/')[-1]))

    with open('bitquery_info.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data[0].keys())

        for contract_data in data:
            csv_writer.writerow(contract_data.values())

    print(f'Спарсено за {datetime.now()-start}')


if __name__ == '__main__':
    main()
