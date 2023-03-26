from typing import Any, Dict, Tuple, List
from AutoUploader import upload_file, parse_response
from AutoDownloader import download_algorithms
from Submission import Submission
import os
import sys
import json
from dotenv import load_dotenv
#    ^^^^^^
# pip install python-dotenv
from random import randint, uniform, gauss
#                                    ^^^^^
# this, and possilby other random functions, may be used to get better params

# information for the upload and download functions
STRATEGY_PATH = "Hyper_Opt_Strategies/Example_Tunable_Strat.py"
STRATEGY_NAME = "Example_Tunable_Strat.py"
ROUND_TO_DOWNLOAD = "ROUND3"

# make a dot env file in this directory called ".env" and put your auth token in it, such as AUTH_TOKEN=0gj20f92efi1093i4jr9qjfqefoidnofieqnfoi
load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# the limits for the params you want to test
# the first value is the minimum, the second is the maximum
# these strings and the types inside the tuple limit should match the params in the strategy file
PARAM_LIMITS = {
    "BUY_QUANTITY": (1, 10),
}

def blast_submission(strategy_path: str, strategy_name: str, auth_token: str, num_submissions: int, param_limits: Dict[str, Tuple[Any, Any]]) -> bool:
    # duplicate the strategy file to be able to change the params
    with open(strategy_path, "r") as f:
        base_strategy = f.read()
    new_strategy_name = strategy_name.replace(".py", "_Copy.py")
    new_strategy_path = "Tuned_Copies/" + new_strategy_name
    try:
        with open(new_strategy_path, "x") as f:
            f.write(base_strategy)
    except FileExistsError:
        with open(new_strategy_path, "w") as f:
            f.write(base_strategy)
    
    # change the params and upload the new strategy
    for i in range(num_submissions):

        # read in the copied strategy
        with open(new_strategy_path, "r") as f:
            new_strategy = f.readlines()

        # change the params
        time_to_modify = False
        for i, line in enumerate(new_strategy):
            if '#PARAMS' in line:
                time_to_modify = True
                continue
            if time_to_modify:
                for param in param_limits:
                    if param in line:
                        space_before_param = new_strategy[i][:new_strategy[i].find(param)]
                        if isinstance(param_limits[param][0], int):
                            new_strategy[i] = space_before_param + param + " = " + str(randint(param_limits[param][0], param_limits[param][1])) + "\n"
                        elif isinstance(param_limits[param][0], float):
                            new_strategy[i]= space_before_param + param + " = " + str(uniform(param_limits[param][0], param_limits[param][1])) + "\n"
                        elif isinstance(param_limits[param][0], bool):
                            new_strategy[i] = space_before_param + param + " = " + str(randint(0, 1)) + "\n"
                        else:
                            raise TypeError("Param type not supported")
                        break
            if '#ENDPARAMS' in line:
                break

        # write the new strategy to the file
        with open(new_strategy_path, "w") as f:
            f.writelines(new_strategy)

        # upload the new strategy
        upload_response = upload_file(new_strategy_path, new_strategy_name, auth_token)
        if upload_response[0] != 200:
            print("Upload failed")
            print(parse_response(upload_response[0], upload_response[1]))
            return False

    return True
    
def sort_submissions_by_profit(submissions: List[Submission]) -> List[Submission]:
    return sorted(submissions, key=lambda submission: submission.fetch_performance(AUTH_TOKEN)[-1][1] if len(submission.fetch_performance(AUTH_TOKEN)) > 0 else 0, reverse=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3", sys.argv[0], "<action: blast_submission, save_results>")
        sys.exit(1)

    if sys.argv[1] == "blast_submission":
        # modify the number of submissions you want to upload here        v
        assert(blast_submission(STRATEGY_PATH, STRATEGY_NAME, AUTH_TOKEN, 1, PARAM_LIMITS))
    elif sys.argv[1] == "save_results":
        submissions = download_algorithms(AUTH_TOKEN, ROUND_TO_DOWNLOAD)
        submissions = sort_submissions_by_profit(submissions)

        with open("Results.txt", "w") as f:
            for i, submission in enumerate(submissions):
                f.write(str(submission) + "\n")
                performance = submission.fetch_performance(AUTH_TOKEN)
                f.write("Profit/Loss: " + (str(performance[-1][1]) if len(performance) > 0 else "Unknown") + "\n")
                # search through submission.file_content for the params
                # write the params to the file
                params: Dict[str, Any] = {}
                params_started = False
                for line in submission.file_content.splitlines():
                    if "#PARAMS" in line:
                        params_started = True
                        continue
                    if params_started:
                        if "#ENDPARAMS" in line:
                            break
                        for param in PARAM_LIMITS:
                            if param in line:
                                if line.find(" = ") == -1:
                                    raise Exception("Param not formatted correctly, should be PARAM = value")
                                params[param] = line[line.find(" = ") + 3:]
                                break
                params_json = json.dumps(params, indent=4)
                f.write("Params:\n")
                f.write(params_json)
                f.write("\n\n")
