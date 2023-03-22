import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMzFlOTg5Mi02MTVlLTQ3ZjQtOGZmZS1hM2M0MTkyYjUzMmIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6ImEzMWU5ODkyLTYxNWUtNDdmNC04ZmZlLWEzYzQxOTJiNTMyYiIsIm9yaWdpbl9qdGkiOiI4OWMzZDNjNy0yMGNmLTQ3YzQtODRlOC1mNjhlYmMxNDFlMmMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiODY3MjlhZDYtZDZlNS00ZTJkLTkyYmUtNDdmYzY0YTNkZjQ4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MTQzOTYsImV4cCI6MTY3OTQzMDYyNywiaWF0IjoxNjc5NDI3MDI3LCJqdGkiOiIwY2UxYTQ4NS03YWIyLTQxYzItODY1NC01OTIwMDc2MjA1ODYiLCJlbWFpbCI6ImphY2subWFuc2ZpZWxkQGxpdmUuY29tIn0.AaXwFn3JsmAyTfW8KnEDKTRxzOF_uYRANS680HTBsTLRqEw2sjHCzd-rZqdLTlAHeFihgvGgy0GDSvlGeErPD37Ui_dN5b_hw7ckJ1aWypNmKuqxYwl_pABqGeVpFH_eW73k4bDj0BttZNFmIt5GElfcBwPYP3A8z7j94kLO1tsvI4M404v4V3-bv3o3Vs8OkBSlJeABtIVrOPBUCap-9loy4S5jXMfiyG0pctZhj7_-JQdjcgXwXVamXiIqE8oT5Fpcmlh6_WvaARvpVVwchIsJcyqQ_6tw5irN3TgB4HTVCxsB3MLmT_q8E59Ls2hx2HCn20Xb8NjCalQzJhmL3A'
Log_file_name = '4d29c1d1-7a9a-4b4f-ad96-ffcb35a29d72'
headers = {
    'authorization': 'Bearer '+ Cookie_id_token,
}

Response = requests.get(
    f'https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/{Log_file_name}',
    headers = headers,
)
print(Response.text)
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