import requests
from Submission import Submission
from typing import List, Tuple
import sys

base_url = "https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod"

def download_algorithms(auth_token: str, round: str) -> List[Submission]:
    response = requests.get(base_url + "/submission/algo/" + round, headers={'authorization': "Bearer " + auth_token})
    
    if response.status_code != 200:
        raise Exception("Failed to fetch submissions: " + response.text)
    
    return [Submission.from_json(x) for x in response.json()]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 " + sys.argv[0] + " <auth_token> <round>")
        exit(1)
        
    auth_token = sys.argv[1]
    round = sys.argv[2]
    
    submissions = download_algorithms(auth_token, round)
    
    for submission in submissions:
        print(submission)
