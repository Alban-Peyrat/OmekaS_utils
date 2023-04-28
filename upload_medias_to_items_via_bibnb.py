# -*- coding: utf-8 -*- 

# Dev for XLSX using pandas, might work on other format

# external imports
import os
from dotenv import load_dotenv
import pandas as pd
import logging
import requests
import json
from omeka_s_tools.api import OmekaAPIClient

# Internal import
import logs

# ----------------- Init -----------------

# Load env var
load_dotenv()

log_path = os.getenv("LOGS_FOLDER")
omeka_url = os.getenv("OMEKA_URL")
key_identity = os.getenv("OMEKA_KEY_IDENTITY")
key_credential = os.getenv("OMEKA_KEY_CREDENTIAL")
output_path = os.getenv("OUTPUT_FOLDER")

# Gets the media list path (xlsx)
input_file = input("Full path to the file with data (must be an XSLX) :\n")
# input_file = os.getenv("TEMP_INPUT_FILE") # temp

# Leaves if the file doesn't exists
if not os.path.exists(input_file):
    print("Error : provided file does not exist")
    exit()

# Gets the files folder path
files_folder = input("Full path to the folder containing the files :\n")
# files_folder = os.getenv("TEMP_FILES_FOLDER") # temp

# Leaves if the file doesn't exists
if not os.path.exists(files_folder):
    print("Error : provided folder does not exist")
    exit()

# Asks for the groups taht will be added
omeka_groups = input("Omeka-S group ID to add (coma separated) : \n")

# Generates the payload
payload = {"o-module-group:group":[]}
for group in omeka_groups.split(","):
    try:
        group = int(group.strip())
    except ValueError:
        continue
    payload["o-module-group:group"].append({"o:id":str(group)})
# Public or not
if payload["o-module-group:group"]:
    payload["o:is_public"] = False
else:
    payload["o:is_public"] = True

# Creates output dir if needed
if not os.path.exists(output_path):
   os.makedirs(output_path)
# Creates logs dir if needed
if not os.path.exists(log_path):
   os.makedirs(log_path)

# Creates the media post file
out_media = open(output_path + "/out_media.json", mode="w", encoding="utf-8") # DON'T FORGET ME
out_media.write("[")
# Creates the CSV output
csv_ouput = open(output_path + "/results.csv", mode="w", encoding="utf-8") # DON'T FORGET ME
csv_ouput.write("file_name;bibnb;id_item;status;id_media\n")

# # Loads the input file
# df = None
# if FILE_FORMAT in ["xlsx", "xls", "ods"]:
#     df = pd.read_excel(INPUT_FILE)
# elif FILE_FORMAT == "csv":
#     df = pd.read_csv(INPUT_FILE, sep=";")
# elif FILE_FORMAT in ["tsv", "txt"]:
#     df = pd.read_csv(INPUT_FILE, sep="\t")
# else:
#     print("Incorrect file format")
#     exit()

# Loads the input file
df = pd.read_excel(input_file, usecols=["file_name", "bibnb", "id_item"],
                   dtype={"file_name": str, "bibnb": str, "id_item": str})

# Everythin is OK, init the logger
service = "Omeka-S_-_Upload_medias_to_items_via_bibnb"
logs.init_logs(log_path, service,'DEBUG')
logger = logging.getLogger(service)
logger.info("All files and folders were successfully found")
logger.info(f"Payload succesfully created : {str(payload)}")

# ----------------- Main -----------------
logger.info("Starting main function...")
errors = {
    "cell_nan":"At least one column has no value",
    "no_file":"Provided file does not exist",
    "get_item":"An error occured trying to get the item",
    "wrong_bibnb":"The biblionumber provided is different from the one associated with the item",
    "post_file":"An error occured trying to upload the file"
}

# Init the omeka client
omeka = OmekaAPIClient(omeka_url + "/api", key_identity=key_identity, key_credential=key_credential)

# For each row
for index, row in df.iterrows():
    logger.info(f"--- Starting Row {index} : biblionumber {row['bibnb']} - item ID {row['id_item']} - file : {row['file_name']}")
    
    # Skips if one value is missing
    if row.isna().any():
        logger.error(errors["cell_nan"])
        csv_ouput.write(f"{';'.join(str(cell) for cell in row)};Error;{errors['cell_nan']}\n") #str(cell) bc nan is float
        continue

    # Skips if the file doesn't exists
    if not os.path.exists(files_folder + "/" + row["file_name"]):
        logger.error(errors["no_file"])
        csv_ouput.write(f"{';'.join(cell for cell in row)};Error;{errors['no_file']}\n")
        continue

    # Gets the item to check if the bibnb is correct
    try:
        item = omeka.get_resource_by_id(row["id_item"], "items")
    except requests.exceptions.RequestException as generic_error:
        logger.error("{} : {} {} : {}".format(errors['get_item'],
                                              str(generic_error.response.status_code),
                                              str(generic_error.response.reason),
                                              str(generic_error.response.text)))
        csv_ouput.write(f"{';'.join(cell for cell in row)};Error;{errors['get_item']}\n")
        continue
    
    logger.info("Item found")

    # Checks if the provided bibnb equals the one in Omeka
    if item["koha:biblionumber"][0]["@value"] != row["bibnb"]:
        logger.error(f"{errors['wrong_bibnb']} : {item['koha:biblionumber'][0]['@value']}")
        csv_ouput.write(f"{';'.join(cell for cell in row)};Error;{errors['wrong_bibnb']}\n")
        continue
    
    # Adds the file with the payload to the item
    try:
        media = omeka.add_media_to_item(row["id_item"], files_folder + "/" + row["file_name"], payload=payload)
    except requests.exceptions.RequestException as generic_error:
        logger.error("{} : {} {} : {}".format(errors['post_file'],
                                              str(generic_error.response.status_code),
                                              str(generic_error.response.reason),
                                              str(generic_error.response.text)))
        csv_ouput.write(f"{';'.join(cell for cell in row)};Error;{errors['post_file']}\n")
        continue
    
    # Success <(^-^)>
    out_media.write(json.dumps(media) + ",")
    logger.info(f"Media successfully created : {str(media['o:id'])}")
    csv_ouput.write(f"{';'.join(cell for cell in row)};Success;{str(media['o:id'])}\n")

logger.info("Main function just ended")

# Clean and closes media file
out_media.seek(out_media.tell() - 1, 0)
out_media.truncate()
out_media.write("]")
out_media.close()
# Closes the CSV output
csv_ouput.close()

logger.info("<(^-^)> <(^-^)> Script fully executed without errors <(^-^)> <(^-^)>")
# __/!\\__ Faut-il rajouter un intervalle entre chaque appel ?