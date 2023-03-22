import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5ZDg2ZmJmZC00MGViLTRjY2UtYTExNS03ODYyYWFkMDVhN2MiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjlkODZmYmZkLTQwZWItNGNjZS1hMTE1LTc4NjJhYWQwNWE3YyIsIm9yaWdpbl9qdGkiOiJkMDFjODNjNy0zYTZiLTQyZGItOTFmZC1hOThkYTc4NDAxNWIiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiZTQyMmZmMGUtMzFlNy00YjlkLTg5ZWYtNWVjZmZjZTdmMjhkIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MjkyODMsImV4cCI6MTY3OTUwOTUyMywiaWF0IjoxNjc5NTA1OTIzLCJqdGkiOiIxYzgyNTgwYS0zMmZkLTRmMTItYmRiOC0yZjYwNGJlM2YxOTgiLCJlbWFpbCI6InJ5YW5jcml2QGdtYWlsLmNvbSJ9.a0ANrN89tVXN_9gvAGZgXBHzDdpoCxTxEv5yyv7ZOrCfOT3XBgunAMeTiD8IVs8mphm7Vejn8YEit_5Wp3DLssfkYqczlJTNmoxRMlJCLRga0pHOO39vV3uNnecw5MhI0iCdLIphGRzxxJnYaBt22L753A3ktyqDmZOsT52lvOX-b-BpRh1bwOvDHi0wi-4DPeUN-aZ7_ze6TFcDs7_OabqIYOyK6u3yVfjT9L95y5vQcJPkB8__WMnYtFzxSXgDjL3gyHdNEYtbEG3ZfWCHXYW4KbRfwuUT9kpHJ8mwM3o4-zDG1Ndu9quXnaE_s6mJ_XvD9nhwqLTO0NCPTmqZxw'
Log_file_name = '4cbd6a4e-4b38-4dff-ab90-e7be89b1f97d'
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