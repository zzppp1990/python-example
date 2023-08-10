import json

#request_json = { "sceneCodes": [ "11-7" ], "username": "zhang0616_test"}
request_json = { "configType":2, "sceneCodes": [ "11-7" ], "username": ""}

try :
    logical_scenario_list = request_json.get("sceneCodes")
    config_type = request_json.get("configType")
    user_id = request_json.get("jobNumber")
    user_name = request_json.get("username")
    print(config_type)
    if logical_scenario_list == '' or config_type == '' or user_id == '' or user_name == '' or  logical_scenario_list == None or config_type == None or user_id == None or user_name == None:
        print("Parameter configuration file error, please check whether the parameter configuration file and sampling method match.")
except Exception as e:
    print(e)