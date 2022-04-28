import requests

BIT_QUERY_API_KEY = ''

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


def get_calls(txn):

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
    nodes, edges = [], []

    calls = {}
    for cc in contractCalls:
        contract = cc['smartContract']['address']['address']
        caller = cc['caller']['address']
        couple = f'{caller}->{contract}'
        if couple in calls:
            calls[couple] += 1
        else:
            calls[couple] = 1

    return calls


def main():

    calls = {}
    for txn in txns:
        new_calls = get_calls(txn)
        for couple in new_calls.keys():
            if couple in calls.keys():
                calls[couple] += new_calls[couple]
            else:
                calls[couple] = new_calls[couple]

    calls = sorted(calls.items(), key=lambda kv: kv[1], reverse=True)


    # calls используем в анализе в jupyter ноутбуке
    print(calls)


if __name__ == '__main__':
    main()
