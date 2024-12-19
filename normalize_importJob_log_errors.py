# -*- coding: utf-8 -*- 

# external imports
import os
import csv
from enum import Enum
import re
import requests
from omeka_s_tools.api import OmekaAPIClient
import dotenv
from typing import Dict, List
import json

# Internal import
import archires_coding_convention_resources as accr
from Koha_API_PublicBiblio import Koha_API_PublicBiblio

# ----------------- Mappings -----------------
class CSV_Headers(Enum):
    ITEM_ID = "item_id"
    BIBNB = "bibnb"
    ERROR = "error"
    ERROR_MSG = "error_msg"
    SCHOOL = "school"
    TITLE = "title"
    MEDIA = "media"
    ITEM_SETS = "item_sets"
    KOHA_RECORD = "koha_record"
    KOHA_EXPORT_OMEKA = "koha_export_omeka"

class Error_types(Enum):
    WOULD_HAVE_BEEN_DELETED = 0
    WILL_BE_IMPORTED = 1
    HAS_BEEN_IMPORTED = 2
    WAS_CREATED = 3

class Detect_Error_Type(Enum):
    WOULD_HAVE_BEEN_DELETED = "would have been deleted"
    WILL_BE_IMPORTED = "will be imported into"
    HAS_BEEN_IMPORTED = "has been imported into"
    WAS_CREATED = "koha:biblionumber property but it was created from"

class Errors_Extract_Data_Regexp(Enum):
    # ↓ $1 = item ID, $2 = biblionumber
    WOULD_HAVE_BEEN_DELETED = r"INFO \(6\): Item (\d+) would have been deleted \(biblionumber: (\d+)"
    # ↓ $1 = item ID, $2 = biblionumber, $3 = biblionumber, $4 = reference ID
    WILL_BE_IMPORTED = r"WARN \(4\): Item (\d+) has value (\d+) in one of its koha:biblionumber property but biblio (\d+) will be imported into item (\d+)$"
    # ↓ $1 = item ID, $2 = biblionumber, $3 = biblionumber, $4 = reference ID
    HAS_BEEN_IMPORTED = r"WARN \(4\): Item (\d+) has value (\d+) in one of its koha:biblionumber property but biblio (\d+) has been imported into item (\d+)$"
    # ↓ $1 = item ID, $2 = biblionumber, $3 original biblionumber
    WAS_CREATED = r"WARN \(4\): Item (\d+) has value (\d+) in one of its koha:biblionumber property but it was created from biblio (\d+)$"

# ----------------- Class def -----------------
class Item_Set_Index(object):
    def __init__(self, omeka_client:OmekaAPIClient):
        self.omeka_client = omeka_client
        self.index:Dict[str, str] = {}
    
    def add_item_set(self, id:str):
        if id in list(self.index.keys()):
            return
        item_set = self.omeka_client.get_resource_by_id(id, "item_sets")
        if item_set:
            if "o:title" in item_set:
                self.index[id] = item_set["o:title"]
    
    def get_item_set_name_by_id(self, id:str) -> str|None:
        if id in list(self.index.keys()):
            return self.index[id]
        return None

# ----------------- Func def -----------------
def default_output_line(line: dict) -> dict:
    """Gives defauts values to non assigned keys"""
    for col in CSV_Headers:
        if col.value not in line:
            line[col.value] = "err"
    return line

# ----------------- Init -----------------

# Loads env var
dotenv.load_dotenv()

OMEKA_URL = os.getenv("OMEKA_URL")
KEY_IDENTITY = os.getenv("OMEKA_KEY_IDENTITY")
KEY_CREDENTIAL = os.getenv("OMEKA_KEY_CREDENTIAL")
INPUT_FILE = os.getenv("NIJLE_INPUT_FILE")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
KOHA_URL = os.getenv("KOHA_URL")

# Leaves if the input file doesn't exists
if not os.path.exists(INPUT_FILE):
    print("Error : provided file does not exist")
    exit()

# Loads the input file
lines = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Checks if data is in the file
if not len(lines) > 0:
    print("Error : provided file has no data")
    exit()

# Erase trailing slashes from OUTPUT_FOLDER and LOG_PATH
OUTPUT_FOLDER = accr.erase_trailing_slash(OUTPUT_FOLDER)
# Creates output dir if needed
if not os.path.exists(OUTPUT_FOLDER):
   os.makedirs(OUTPUT_FOLDER)

# Creates the output file
OUTPUT_FILE = open(OUTPUT_FOLDER + "/importJob_errors.csv", "w", newline="", encoding="utf-8") # DON'T FORGET ME
CSV_WRITER = csv.DictWriter(OUTPUT_FILE, extrasaction="ignore", fieldnames=[elem.value for elem in CSV_Headers], delimiter=";")
CSV_WRITER.writeheader()

# ----------------- Main -----------------
# Init the omeka client
OMEKA = OmekaAPIClient(OMEKA_URL + "/api", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)
ITEM_SET_INDEX = Item_Set_Index(OMEKA)

for line in lines:
    for error in Error_types:
        # The line is one of the supported errors
        if Detect_Error_Type[error.name].value in line:
            output = {}
            output[CSV_Headers.ERROR.value] = error.name
            pattern = Errors_Extract_Data_Regexp[output[CSV_Headers.ERROR.value]].value
            regex_matched = re.search(pattern, line)
            if regex_matched:
                output[CSV_Headers.ITEM_ID.value] = regex_matched.group(1)
                bibnb = regex_matched.group(2)
                output[CSV_Headers.BIBNB.value] = bibnb
                # Generate the error message
                if error == Error_types.WOULD_HAVE_BEEN_DELETED:
                    output[CSV_Headers.ERROR_MSG.value] = "Should be deleted"
                elif error == Error_types.WILL_BE_IMPORTED or error == Error_types.HAS_BEEN_IMPORTED:
                    output[CSV_Headers.ERROR_MSG.value] = regex_matched.group(4) + " is reference item"
                elif error == Error_types.WILL_BE_IMPORTED or error == Error_types.HAS_BEEN_IMPORTED:
                    output[CSV_Headers.ERROR_MSG.value] = regex_matched.group(3) + " is original bibblionumber"
                try:
                    item = OMEKA.get_resource_by_id(output[CSV_Headers.ITEM_ID.value], "items")
                except requests.exceptions.RequestException as generic_error:
                    output = default_output_line(output)
                else:
                    try:
                        output[CSV_Headers.TITLE.value] = item["o:title"]
                        output[CSV_Headers.SCHOOL.value] = item["dcterms:provenance"][0]["@value"]
                        output[CSV_Headers.MEDIA.value] = len(item["o:media"]) > 0
                        output[CSV_Headers.ITEM_SETS.value] = []
                        for item_set in item["o:item_set"]:
                            ITEM_SET_INDEX.add_item_set(item_set["o:id"])
                            output[CSV_Headers.ITEM_SETS.value].append(ITEM_SET_INDEX.get_item_set_name_by_id(item_set["o:id"]))
                        koha_record = Koha_API_PublicBiblio(bibnb, KOHA_URL, format="application/marc-in-json")
                        output[CSV_Headers.KOHA_RECORD.value] = koha_record.get_init_status() == "Success"
                        if koha_record.get_init_status() == "Success":
                            for field in json.loads(koha_record.record)["fields"]:
                                if "099" in field.keys():
                                    for subfield in field["099"]["subfields"]:
                                        code = list(subfield.keys())[0]
                                        if code == "x" :
                                            output[CSV_Headers.KOHA_EXPORT_OMEKA.value] = subfield[code]
                            if not CSV_Headers.KOHA_EXPORT_OMEKA.value in output:
                                output[CSV_Headers.KOHA_EXPORT_OMEKA.value] = "no 099$x"

                    except:
                        output = default_output_line(output)
            else:
                output = default_output_line(output)
            CSV_WRITER.writerow(output)

# Close errors file
OUTPUT_FILE.close()
