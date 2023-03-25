# Upload a file to the IMC API for testing
# Can be run as a script or imported as a module

import pycurl
from io import BytesIO
import sys
import os
import json
from typing import Tuple

url = "https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/submission/algo"
headers = {
    'authority': 'bz97lt8b1e.execute-api.eu-west-1.amazonaws.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.5',
    'authorization': 'Bearer ',
    'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary0BqsYt5stBH1nJVM',
    'origin': 'https://prosperity.imc.com',
    'referer': 'https://prosperity.imc.com/',
    'sec-ch-ua': '"Not_A Brand";v="99", "Brave";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)' + \
    ' "Chrome/109.0.0.0 Mobile Safari/537.36',
}

def upload_file(file_path: str, file_name: str, auth_token: str) -> Tuple[int, str]:
    """
    Uploads a file using the IMC API
    
    Parameters:
    file_path (str): The path to the file to upload.
    file_name (str): The name of the file to upload. This is the name that will be displayed on the IMC website.
    auth_token (str): The authentication token to use for the upload.
    
    Returns:
    Tuple[int, str]: A tuple containing the response code and the response from the IMC API.
    """
    # Read file
    file_content = open(file_path).read()
    headers['authorization'] = 'Bearer ' + auth_token

    # Create body
    body = "------WebKitFormBoundary0BqsYt5stBH1nJVM\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" \
    + file_name + "\"\r\nContent-Type: text/x-python\r\n\r\n\r\n" \
    + file_content + "\r\n\r\n------WebKitFormBoundary0BqsYt5stBH1nJVM--" \

    # Encode body as a file object
    body_as_file = BytesIO(body.encode('utf-8'))

    # Set curl options and make request
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEDATA, buffer)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, [k + ': ' + v for k, v in headers.items()])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.READDATA, body_as_file)
    c.perform()
    
    response = buffer.getvalue().decode('utf-8')
    response_code = c.getinfo(pycurl.RESPONSE_CODE)

    # Close connection
    c.close()
    
    return response_code, response

def parse_response(response_code: int, response: str) -> str:
    """
    Parses the response from the IMC API and returns a human-readable string describing the response.
    
    Parameters:
    response_code (int): The response code from the IMC API.
    response (str): The response from the IMC API.
    
    Returns:
    A small string describing the response.
    
    """
    response_json = json.loads(response)
    
    if response_json['message'] == "Your algorithm was submitted.":
        return "Success"
    elif response_json['message'] == "The incoming token has expired":
        return "Token has expired"
    elif response_json['message'] == "The provided file is too small. Please upload a file of at least 100 bytes.":
        return "File is too small"
    elif response_json['message'] == "Unauthorized":
        return "Invalid token"
    elif response_json['message'] == "The provided file is too large. Please upload a file of 100kB or less.":
        return "File is too large"
    else:
        return "Unknown response"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3", sys.argv[0], "<auth_token> <file>")
        exit(1)

    auth_token = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print("File", file_path, "does not exist")
        exit(2)

    file_name = os.path.basename(file_path)
    
    response_code, response = upload_file(file_path, file_name, auth_token)
    print("Response", response)
    print("Response code", response_code)
    print(parse_response(response_code, response))
    
    if response_code != 200:
        exit(3)
