import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMzFlOTg5Mi02MTVlLTQ3ZjQtOGZmZS1hM2M0MTkyYjUzMmIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6ImEzMWU5ODkyLTYxNWUtNDdmNC04ZmZlLWEzYzQxOTJiNTMyYiIsIm9yaWdpbl9qdGkiOiI4OWMzZDNjNy0yMGNmLTQ3YzQtODRlOC1mNjhlYmMxNDFlMmMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiODY3MjlhZDYtZDZlNS00ZTJkLTkyYmUtNDdmYzY0YTNkZjQ4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MTQzOTYsImV4cCI6MTY3OTQ0ODcyNywiaWF0IjoxNjc5NDQ1MTI3LCJqdGkiOiIxN2QxMGE5MS04Y2RmLTRjY2UtODIwZS0zYmIzNmUyNmNiOTciLCJlbWFpbCI6ImphY2subWFuc2ZpZWxkQGxpdmUuY29tIn0.OluMbby_vZstSugtAfiqX93nhRRZ0PpwhedlHCPiDu0Xj8XGiGCv5utB5irs71rbvbOCpYs2qWzM0wFRDrV0HQp_zz0Fs0rBGtt1T4o6erwS13pbDJ520iDKdzdMoB4sOOgTEj3_HoNGla1ncMOciaazk9sv2vuHZPbfWP8dWnYAXVw95WEsM4iKQTA2J7apKnaU11Fud1rlytQxUhbjCZWU6eKmnH0U4tWXwe77SCpB_asgAwZbNBpYh0JlXV0hqZ-vM8TzuOaqqMRv9UEepfBSR8f51dbteelbr1gOIQ0FGY-G4rBZxhWuHcPCca6GY69xUCjW9rP8Kpv1O7l0Yw'
Log_file_name = 'a9255763-e32f-4bb4-a8f6-531b8efbb8cf'
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