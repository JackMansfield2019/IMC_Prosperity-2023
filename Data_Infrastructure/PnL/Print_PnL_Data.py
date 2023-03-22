import requests
import json
Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5ZDg2ZmJmZC00MGViLTRjY2UtYTExNS03ODYyYWFkMDVhN2MiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjlkODZmYmZkLTQwZWItNGNjZS1hMTE1LTc4NjJhYWQwNWE3YyIsIm9yaWdpbl9qdGkiOiJkMDFjODNjNy0zYTZiLTQyZGItOTFmZC1hOThkYTc4NDAxNWIiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiZTQyMmZmMGUtMzFlNy00YjlkLTg5ZWYtNWVjZmZjZTdmMjhkIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MjkyODMsImV4cCI6MTY3OTUxNjc2NCwiaWF0IjoxNjc5NTEzMTY1LCJqdGkiOiJiYjE4ZGU2Ni01OTMyLTRmMjgtOTkzMS01NjUxN2I4NGZkYWMiLCJlbWFpbCI6InJ5YW5jcml2QGdtYWlsLmNvbSJ9.dtOmEJO0VFv0bS2JTrYU2P6DnC0G9W6Vsl2Hk8Nso56s04_vRvdU0H9L8qJuNWkRQe-892m0qZ-IR0mOsMLF78an8NSfLS9Yd9YBxzIrwOpQUtthFMIvrFl_rPUhDcSurc9UcnrhSdEutG2Gy9fPiPoZbqP9L-wex4J8UhLSGTlEgw8N4T6moLooIfRpNqmg4IzanjbhTCzN6EdPYNGUa_ZIwTBivN7X8msaheqFUxPOWSCt7J_VCod14Y9ZE7yJWSBHZesYXf7mhHL08Lx-3hgVEQVQ7VoVuCAAe8r9SeO_4YzuG-P_stfOoDOvXL-Ow10FTzVkvPhpzPmV-AjFag'
Log_file_name = '1842abfc-336b-4f36-8ff5-3b07389ad76f'
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
    # plt.savefig('Round_1_graph')
plot_timestamp_value(timestamp, price)