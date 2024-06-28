# from Sismedia.RetrieveToken import update_token_env
# from Database.DbConnection import client
from Database.GenerateInserts import process_all_json_files
from Database.RetrieveDevices import retrive_devices
from Database.UnifyJsons import get_unified_jsons
from Sismedia.RetrieveData import process_devices
from Sismedia.RetrieveToken import update_token_env

if __name__ == '__main__':
    update_token_env()
    retrive_devices()
    process_devices()
    get_unified_jsons()
    process_all_json_files()
    # update_token_env()
    # print(client)
