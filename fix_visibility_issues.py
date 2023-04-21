# -*- coding: utf-8 -*- 

# external imports
import json
import os
import requests
from omeka_s_tools.api import OmekaAPIClient

# Internal import

# Loads settings
with open('./settings.json', "r+", encoding="utf-8") as f:
    settings = json.load(f)

omeka_url = settings["OMEKA_URL"]
key_identity = settings["KEY_IDENTITY"]
key_credential = settings["KEY_CREDENTIAL"]
output_path = settings["OUTPUT_FOLDER"]

# Get the items ID list path
items_list_file = input("Full path to the items ID list (\\n as a separator) :\n")

# Leaves if the file doesn't exists
if not os.path.exists(items_list_file):
    print("Error : provided file does not exist")
    exit()

# Creates output dir if needed
if not os.path.exists(output_path):
   os.makedirs(output_path)

# Stores the items ID list
with open(items_list_file, mode="r", encoding="utf-8") as f:
    items_id_list = f.readlines()

jobs = {
    "0" : "Spread item visibility to medias",
    "1" : "Clean item visibility"
    }

# Gets the job to execute
job = input("Which job should be executed (input the number) ?\n{}".format("".join(key + " : " + value + "\n" for key, value in jobs.items())))

# Leaves if the job is incorect
if job not in jobs:
    print("Job does not exist :", str(job))
    exit()
elif job == "0":
    # Creates the medias files
    out_media_get = open(output_path + "/media_get.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    out_media_post = open(output_path + "/media_post.json", mode="w", encoding="utf-8") # DON'T FORGET ME
    out_media_get.write("[")
    out_media_post.write("[")


def finish_file(f):
    """Removes the last comma and wirte a final "]"
    Takes an opened file as an argument."""
    f.seek(f.tell() - 1, 0)
    f.truncate()
    f.write("]")

# Init the omeka client
omeka = OmekaAPIClient(omeka_url + "/api", key_identity=key_identity, key_credential=key_credential)

# Creates the items files
with open(output_path + "/item_get.json", mode="w", encoding="utf-8") as out_item_get:
    out_item_get.write("[")
    with open(output_path + "/item_post.json", mode="w", encoding="utf-8") as out_item_post:
        out_item_post.write("[")
        for id in items_id_list:
            id = id.strip()
            # Gets the item
            try:
                item = omeka.get_resource_by_id(id, "items")
            except requests.exceptions.RequestException as generic_error:
                out_item_get.write("{\"" + id + "\":\"" + str(generic_error) + "\"},")
            else:
                out_item_get.write(json.dumps(item) + ",")

                # If spread_item
                if job == "0":
                    # Gets group data
                    groups = item["o-module-group:group"]
                    
                    # For each media
                    for media_ids in item["o:media"]:
                        # Gets the media
                        try:
                            media = omeka.get_resource_by_id(media_ids["o:id"], "media")
                        except requests.exceptions.RequestException as generic_error:
                            out_media_get.write("{\"" + str(media_ids["o:id"]) + "\":\"" + str(generic_error) + "\"},")
                        else:
                            out_media_get.write(json.dumps(media) + ",")

                            # Changes group data and public
                            media["o-module-group:group"] = groups
                            # Stringifies groups o:id to prevent error 500
                            for group in groups:
                                group["o:id"] = str(group["o:id"])
                            media["o:is_public"] = False

                            # Posts the media
                            try:
                                media_updated = omeka.update_resource(media, "media")
                            except requests.exceptions.RequestException as generic_error:
                                out_media_post.write("{\"" + str(media_ids["o:id"]) + "\":\"" + str(generic_error) + "\"},")
                            else:
                                out_media_post.write(json.dumps(media_updated) + ",")
                
                # Changes group data and public
                item["o-module-group:group"] = []
                item["o:is_public"] = True

                # Posts the media
                try:
                    item_updated = omeka.update_resource(item, "items")
                except requests.exceptions.RequestException as generic_error:
                    out_item_post.write("{\"" + id + "\":\"" + str(generic_error) + "\"},")
                else:
                    out_item_post.write(json.dumps(item_updated) + ",")

        # Finishes the file
        finish_file(out_item_get)
        finish_file(out_item_post) 

# Closes the media files
if job == "0":
    finish_file(out_media_get)
    out_media_get.close()
    finish_file(out_media_post)
    out_media_post.close()
