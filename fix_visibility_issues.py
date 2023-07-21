# -*- coding: utf-8 -*- 

# external imports
import json
import os
import requests
from omeka_s_tools.api import OmekaAPIClient
import dotenv
import logging

# Internal import
import logs
import archires_coding_convention_resources as accr

# ----------------- Mappings -----------------

JOBS = {
    "0" : {
        "name":"Spread item visibility to medias",
        "get_item":True,
        "post_item":True,
        "get_item_groups":True,
        "get_media":True,
        "post_media":True,
        "get_media_groups":False
        },
    "1" : {
        "name":"Clean item visibility",
        "get_item":True,
        "post_item":True,
        "get_item_groups":False,
        "get_media":False,
        "post_media":False,
        "get_media_groups":False
        },
    "9" : {
        "name":"Add groups to medias by item id",
        "get_item":True,
        "post_item":False,
        "get_item_groups":False,
        "get_media":True,
        "post_media":True,
        "get_media_groups":True
        }
    }

ERRORS = {
    "empty_id":"Provided ID is empty",
    "no_media_to_post":"No media is defined : can't post it",
    "no_item_to_post":"No item is defined : can't post it"
}

# ----------------- Func def -----------------
def finish_file(f):
    """Removes the last comma and wirte a final "]"
    Takes an opened file as an argument."""
    f.seek(f.tell() - 1, 0)
    f.truncate()
    f.write("]")

# ----------------- Init -----------------

# Loads env var
dotenv.load_dotenv()

LOG_PATH = os.getenv("LOGS_FOLDER")
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL")
OMEKA_URL = os.getenv("OMEKA_URL")
KEY_IDENTITY = os.getenv("OMEKA_KEY_IDENTITY")
KEY_CREDENTIAL = os.getenv("OMEKA_KEY_CREDENTIAL")
INPUT_FILE = os.getenv("INPUT_FILE_FIX_VISIBILITY")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")

# Leaves if the file doesn't exists
if not os.path.exists(INPUT_FILE):
    print("Error : provided file does not exist")
    exit()

# Stores the items ID list
OMEKA_ID_LIST = []
with open(INPUT_FILE, mode="r", encoding="utf-8") as f:
    OMEKA_ID_LIST = f.readlines()

# Checks if there's data in the file
if not len(OMEKA_ID_LIST) > 0:
    print("Error : provided file has no data")
    exit()

# Gets the job to execute
job = input("Which job should be executed (input the number) ?\n{}".format("".join(key + " : " + value["name"] + "\n" for key, value in JOBS.items())))

# Leaves if the job is incorect
if job not in JOBS:
    print("Job does not exist :", str(job))
    exit()

print(f"Job : {JOBS[job]['name']}")

# If necessary, asks for the groups that will be added
omeka_groups = []
if job == "9":
    omeka_groups = input("Omeka-S group ID to add (coma separated) : \n")
NEW_GROUPS_ID = []
for group in omeka_groups.split(","):
    try:
        group = int(group.strip())
    except ValueError:
        continue
    NEW_GROUPS_ID.append({"o:id":str(group)})

# Erase trailing slashes from OUTPUT_FOLDER and LOG_PATH
OUTPUT_FOLDER = accr.erase_trailing_slash(OUTPUT_FOLDER)
LOG_PATH = accr.erase_trailing_slash(LOG_PATH)
# Creates output dir if needed
if not os.path.exists(OUTPUT_FOLDER):
   os.makedirs(OUTPUT_FOLDER)
# Creates logs dir if needed
if not os.path.exists(LOG_PATH):
   os.makedirs(LOG_PATH)

# Creates the item and medias files
OUT_ITEM_GET = None
if JOBS[job]["get_item"]:
    OUT_ITEM_GET = open(OUTPUT_FOLDER + "/item_get.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    OUT_ITEM_GET.write("[")
OUT_ITEM_POST = None
if JOBS[job]["post_item"]:
    OUT_ITEM_POST = open(OUTPUT_FOLDER + "/item_post.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    OUT_ITEM_POST.write("[")
OUT_MEDIA_GET = None
if JOBS[job]["get_media"]:
    OUT_MEDIA_GET = open(OUTPUT_FOLDER + "/media_get.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    OUT_MEDIA_GET.write("[")
OUT_MEDIA_POST = None
if JOBS[job]["post_media"]:
    OUT_MEDIA_POST = open(OUTPUT_FOLDER + "/media_post.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    OUT_MEDIA_POST.write("[")

# Creates the error file
ERRORS_FILE = open(OUTPUT_FOLDER + "/errors.csv", "w", encoding="utf-8") # DON'T FORGET ME
ERRORS_FILE.write("index;provided_omeka_id;resource;error\n")

# Sets the logger level
LOGGER_LEVEL = accr.define_logger_level(LOGGER_LEVEL)

# Everythin is OK, init the logger
SERVICE = "Omeka-S_-_Fix_visibility_issues"
logs.init_logs(LOG_PATH, SERVICE, LOGGER_LEVEL)
LOGGER = logging.getLogger(SERVICE)
LOGGER.info("All files and folders were successfully found")
LOGGER.info("All output files were successfully created")
LOGGER.info(f"Job selected : {JOBS[job]['name']}")
if NEW_GROUPS_ID:
    LOGGER.info(f"Specified groups : {JOBS[job]['name']}")

# ----------------- Main -----------------
LOGGER.info("Starting main function...")

# Init the omeka client
OMEKA = OmekaAPIClient(OMEKA_URL + "/api", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)

for index, id in enumerate(OMEKA_ID_LIST):
    LOGGER.info(f"--- Starting ID {index} : {id}")

    id = id.strip()
    if not id:
        LOGGER.error(ERRORS["empty_id"])
        ERRORS_FILE.write(f"{index};{id};unknown;{ERRORS['empty_id']}\n")
        continue

    # If needed, gets the item
    item = None
    if JOBS[job]["get_item"]:
        try:
            item = OMEKA.get_resource_by_id(id, "items")
        except requests.exceptions.RequestException as generic_error:
            LOGGER.error(str(generic_error))
            ERRORS_FILE.write(f"{index};{id};item;{str(generic_error)}\n")
            continue
        else:
            LOGGER.debug(f"Item found : {item['o:id']}")
            OUT_ITEM_GET.write(json.dumps(item) + ",")

    # If needed, gets the item groups
    item_groups = []
    if JOBS[job]["get_item_groups"]:
        item_groups = item["o-module-group:group"]
        LOGGER.debug(f"Item groups : {str(item_groups)}")

    # Prepare the media list for this index
    media_ids = []
    # If the id provided is a media ID, adds it to the list
    if job in []: # No job does that for now
        media_ids.append(id)
    # If the medias ID come from the item, adds them to the list
    elif JOBS[job]["get_item"]:
        for media in item["o:media"]:
            media_ids.append(media["o:id"])

    # --- Media processsing
    for media_id in media_ids:
        # If needed, gets the media
        media = None
        if JOBS[job]["get_media"]:
            try:
                media = OMEKA.get_resource_by_id(media_id, "media")
            except requests.exceptions.RequestException as generic_error:
                LOGGER.error(str(generic_error))
                ERRORS_FILE.write(f"{index};{media_id};media;{str(generic_error)}\n")
                continue
            else:
                LOGGER.debug(f"Media found : {media['o:id']}")
                OUT_MEDIA_GET.write(json.dumps(media) + ",")

        # If needed, gets the media groups
        media_groups = []
        if JOBS[job]["get_media_groups"]:
            media_groups = media["o-module-group:group"]
            LOGGER.debug(f"Media groups : {str(media_groups)}")
        
        if media:
            # Edits the media visibility depending on jobs
            if job == "0":
                media["o-module-group:group"] = item_groups
            elif job == "9":
                media["o-module-group:group"] += NEW_GROUPS_ID
            # Stringifies groups o:id to prevent error 500
            for group in media["o-module-group:group"]:
                group["o:id"] = str(group["o:id"])
            # Chose visibility depending on the presence of groups
            if len(media["o-module-group:group"]) > 0:
                media["o:is_public"] = False

        # If needed, posts the media
        if JOBS[job]["post_media"]:
            if not media:
                LOGGER.error(ERRORS["no_media_to_post"])
                ERRORS_FILE.write(f"{index};{media_id};media;{ERRORS['no_media_to_post']}\n")
                continue
            media_updated = None
            try:
                media_updated = OMEKA.update_resource(media, "media")
            except requests.exceptions.RequestException as generic_error:
                LOGGER.error(str(generic_error))
                ERRORS_FILE.write(f"{index};{media_id};media;{str(generic_error)}\n")
                continue
            else:
                LOGGER.debug(f"Media {media_updated['o:id']} successfully updated")
                OUT_MEDIA_POST.write(json.dumps(media_updated) + ",")
    # --- End of media processing

    if item:
        # Edits the item visibility depending on jobs
        if job in ["0", "1"]:
            item["o-module-group:group"] = []
        # Stringifies groups o:id to prevent error 500
        for group in item["o-module-group:group"]:
            group["o:id"] = str(group["o:id"])
        # Chose visibility depending on the presence of groups
        if len(item["o-module-group:group"]) > 0:
            item["o:is_public"] = False

    # If needed, posts the item
    if JOBS[job]["post_item"]:
        if not item:
            LOGGER.error(ERRORS["no_item_to_post"])
            ERRORS_FILE.write(f"{index};{id};item;{ERRORS['no_item_to_post']}\n")
            continue
        item_updated = None
        try:
            item_updated = OMEKA.update_resource(item, "items")
        except requests.exceptions.RequestException as generic_error:
            LOGGER.error(str(generic_error))
            ERRORS_FILE.write(f"{index};{id};item;{str(generic_error)}\n")
            continue
        else:
            LOGGER.debug(f"Item {item_updated['o:id']} successfully updated")
            OUT_MEDIA_POST.write(json.dumps(item_updated) + ",")
    
    LOGGER.info("ID fully processed")

# Finishes and close get and post files
for f in [OUT_ITEM_GET, OUT_ITEM_POST, OUT_MEDIA_GET, OUT_MEDIA_POST]:
    if f:
        finish_file(f)
        f.close()

# Close errors file
ERRORS_FILE.close()

LOGGER.info("<(^-^)> <(^-^)> Script fully executed without errors <(^-^)> <(^-^)>")