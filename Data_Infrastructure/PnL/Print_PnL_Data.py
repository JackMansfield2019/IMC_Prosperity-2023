import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMzFlOTg5Mi02MTVlLTQ3ZjQtOGZmZS1hM2M0MTkyYjUzMmIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6ImEzMWU5ODkyLTYxNWUtNDdmNC04ZmZlLWEzYzQxOTJiNTMyYiIsIm9yaWdpbl9qdGkiOiI4OWMzZDNjNy0yMGNmLTQ3YzQtODRlOC1mNjhlYmMxNDFlMmMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiODY3MjlhZDYtZDZlNS00ZTJkLTkyYmUtNDdmYzY0YTNkZjQ4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MTQzOTYsImV4cCI6MTY3OTQ2MzE4MiwiaWF0IjoxNjc5NDU5NTgyLCJqdGkiOiIwZWM2Mjc0Ni0wMDJjLTRlYTMtODk5NS1lYzFlMDdkOTYyZTgiLCJlbWFpbCI6ImphY2subWFuc2ZpZWxkQGxpdmUuY29tIn0.QIADl-vzAlrPEcxgZ3pUOm1XDSj2rd35WZGe9B2YmP4WM3l1Vj-pg6P18O7fBp7gUgG4eu0i0KOLD_kGOxjlLpZUcU2hrwNX1ZnDaWnssZ8-yTqBgpgOME8MUoIA3tL3KpyIZz5ktS0Swps42ClrBkSPMnj1VRtFY5QaFVH8D7XvYVscUdobWcYyDfhKB-pX0AlGNXBXFD8_3E_2LxUc5FGiAgle7mtMZWJ34ytnGWCmWQGiXQE2tiLj4Y6E6-doL8O7zCOoKYQG91aQGC_LDY5C8KX5KTGKgHYJhl8AKylpTGQUipcceXATBzx9eeVeZQtsRpF0J8UpkTeuW4VJTw'
Log_file_name = 'f75d5d1b-fe78-43d8-8d28-b8104335ad37'
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
        timestamp_list.append(int(parts[0]))
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
    plt.savefig('EMA8')
plot_timestamp_value(timestamp, price)