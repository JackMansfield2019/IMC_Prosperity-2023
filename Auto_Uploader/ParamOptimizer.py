from typing import Any, Dict, Tuple
from AutoUploader import upload_file, parse_response
from AutoDownloader import download_algorithms
import os
from dotenv import load_dotenv
#    ^^^^^^
# pip install python-dotenv
from random import randint, uniform, gauss
#                                    ^^^^^
# this, and possilby other random functions, may be used to get better params

# information for the upload and download functions
STRATEGY_PATH = "Hyper_Opt_Strategies/Example_Tunable_Strat.py"
STRATEGY_NAME = "Example_Tunable_Strat.py"

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
    
# modify the number of submissions you want to upload here        v
assert(blast_submission(STRATEGY_PATH, STRATEGY_NAME, AUTH_TOKEN, 1, PARAM_LIMITS))
