import requests
from typing import List, Tuple
import matplotlib.pyplot as plt

base_url = "https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod"

class Submission:
    def __init__(self, id: str, round: str, teamId: str, user: dict, timestamp: str, file_name: str,
        file_content: str, status: str, selected: bool):
        self.id = id
        self.round = round
        self.teamId = teamId
        self.user = user
        self.timestamp = timestamp
        self.file_name = file_name
        self.file_content = file_content
        self.status = status
        self.selected = selected
        
    @staticmethod
    def fetch_log_by_id(id: str, auth_token: str) -> str:
        response = requests.get(base_url + "/submission/logs/" + id, headers={'authorization': "Bearer " + auth_token})
        
        if response.status_code != 200:
            raise Exception("Failed to fetch log")

        return response.text
        
        
    def fetch_log(self, auth_token: str) -> str:
        if self.status != "FINISHED":
            return ""
        
        return Submission.fetch_log_by_id(self.id, auth_token)
    
    @staticmethod
    def fetch_performance_by_id(id: str, auth_token: str) -> List[Tuple[float, float]]:
        response = requests.get(base_url + "/results/tutorial/" + id, headers={'authorization': "Bearer " + auth_token})
        
        if response.status_code != 200:
            raise Exception("Failed to fetch performance: " + response.text)
        
        performance = response.json()['algo']['summary']['graphLog'][16:]
        split_performance = performance.strip().split("\n")
        
        time_price = []
        
        for i in range(0, len(split_performance), 2):
            parts = split_performance[i].split(";")
            time_price.append((float(parts[0]), float(parts[1])))
            
        return time_price
        
    def fetch_performance(self, auth_token: str) -> List[Tuple[float, float]]:
        if self.status != "FINISHED":
            return []
        
        return Submission.fetch_performance_by_id(self.id, auth_token)
    
    @staticmethod
    def plot_performance_by_id(id: str, auth_token: str, performance: List[Tuple[float, float]] | None = None) -> None:
        if performance is None:
            performance = Submission.fetch_performance_by_id(id, auth_token)
        
        plt.title("Performance of algorithm " + id, fontsize=16)
        plt.plot([x[0] for x in performance], [x[1] for x in performance])
        plt.suptitle("Total Profit: " + str(performance[-1][1]) + " Seashells")
        plt.xlabel("Time")
        plt.ylabel("Profit (Seashells)")
        plt.show()
        plt.clf()
        
    def plot_performance(self, auth_token: str, performance: List[Tuple[float, float]] | None = None) -> None:
        Submission.plot_performance_by_id(self.id, auth_token, performance)
        
    @staticmethod
    def from_json(json: dict):
        return Submission(json['id'], json['round'], json['teamId'], json['user'], json['timestamp'], json['fileName'],
            json['content'], json['status'], json['selectedForRound'])
        
        
    def __str__(self) -> str:
        return "Algorithm " + self.file_name + " submitted by " + self.user['firstName'] + " at " + self.timestamp + \
        " with id " + self.id
