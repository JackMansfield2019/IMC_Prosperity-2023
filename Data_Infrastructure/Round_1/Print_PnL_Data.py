import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMzFlOTg5Mi02MTVlLTQ3ZjQtOGZmZS1hM2M0MTkyYjUzMmIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6ImEzMWU5ODkyLTYxNWUtNDdmNC04ZmZlLWEzYzQxOTJiNTMyYiIsIm9yaWdpbl9qdGkiOiI4OWMzZDNjNy0yMGNmLTQ3YzQtODRlOC1mNjhlYmMxNDFlMmMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiODY3MjlhZDYtZDZlNS00ZTJkLTkyYmUtNDdmYzY0YTNkZjQ4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MTQzOTYsImV4cCI6MTY3OTQwODk2NSwiaWF0IjoxNjc5NDA1MzY1LCJqdGkiOiIzMTliNDU0OS1iYWQyLTQ3NmUtYjRkNC1jNGNhZTIxYjY0MDQiLCJlbWFpbCI6ImphY2subWFuc2ZpZWxkQGxpdmUuY29tIn0.d5eAlPJ5QniCo2bGwld6J_fLmqLqhpHIlpXZahqdwhkH2C5Rxsir-0V0qB_XhkMFnTQU1hk5TCJgonKLGh9auVw-AZggRFJGZ_dRiFICKAF7551z3QJnF_vrRu0ksIRLggohZ8DToOHk-THtnKsxDh6qftpdBvsBQ8zl4e6NH6Cc9quINKOQImC2jFeD37XAOhwlIOuxdhL7gX7r1msY48tII4dWRYuV57ZoUp4Gl7fLRl1ilUj8tgS6CH6Px4nBYkksHqToLoRTfqHxIbCjCNxno38JY_ea8ce5kUJDArAgam3PaAorUlg7kPhszGv-LRNrxvN_pDcikpgLWGiPTg'
Log_file_name = '7cdf7072-3ee8-4f7b-9921-53fca7a53a9f'
headers = {
    'authorization': 'Bearer '+ Cookie_id_token,
}

Response = requests.get(
    f'https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/{Log_file_name}',
    headers = headers,
)
#print(Response.text)
print(Response.json()['algo']['summary']['graphLog'][16:])

def parse_input_string(input_string,timestamp_list,price_list):
    split_input = input_string.strip().split('\n')
    for i in range(0, len(split_input), 2):
        print(split_input[i])
        parts = split_input[i].split(';')
        timestamp_list.append(parts[0])
        price_list.append(float(parts[1]))
    return timestamp_list, price_list

stringI = Response.json()['algo']['summary']['graphLog'][16:]
timestamp= []
price= []
parse_input_string(stringI,timestamp,price)

import matplotlib.pyplot as plt
import datetime
import os

def plot_timestamp_value(timestamps, values):
    
    # Plot the graph
    plt.plot(timestamps, values)
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.show()
    plt.savefig('Round_1_graph')
plot_timestamp_value(timestamp, price)