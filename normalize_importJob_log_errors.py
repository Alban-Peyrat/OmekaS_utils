# -*- coding: utf-8 -*- 

# external imports
import os
import csv
from enum import Enum
import re
import requests
from omeka_s_tools.api import OmekaAPIClient
import dotenv

# Internal import
import archires_coding_convention_resources as accr

# ----------------- Mappings -----------------
HEADERS = ["item_id", "bibnb", "error", "error_msg", "school", "title"]

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

# ----------------- Func def -----------------
def default_output_line(line: dict) -> dict:
    """Gives defauts values to non assigned keys"""
    for col in HEADERS:
        if col not in line:
            line[col] = "err"
    return line

# ----------------- Init -----------------

# Loads env var
dotenv.load_dotenv()

OMEKA_URL = os.getenv("OMEKA_URL")
KEY_IDENTITY = os.getenv("OMEKA_KEY_IDENTITY")
KEY_CREDENTIAL = os.getenv("OMEKA_KEY_CREDENTIAL")
INPUT_FILE = os.getenv("NIJLE_INPUT_FILE")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")

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
OUTPUT_FILE = open(OUTPUT_FOLDER + "/importJob_errors.csv", "w", encoding="utf-8") # DON'T FORGET ME
CSV_WRITER = csv.DictWriter(OUTPUT_FILE, extrasaction="ignore", fieldnames=HEADERS, delimiter=";")
CSV_WRITER.writeheader()

# ----------------- Main -----------------
# Init the omeka client
OMEKA = OmekaAPIClient(OMEKA_URL + "/api", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)

for line in lines:
    for error in Error_types:
        # The line is one of the supported errors
        if Detect_Error_Type[error.name].value in line:
            output = {}
            output["error"] = error.name
            pattern = Errors_Extract_Data_Regexp[output["error"]].value
            regex_matched = re.search(pattern, line)
            if regex_matched:
                output["item_id"] = regex_matched.group(1)
                output["bibnb"] = regex_matched.group(2)
                # Generate the error message
                if error == Error_types.WOULD_HAVE_BEEN_DELETED:
                    output["error_msg"] = "Should be deleted"
                elif error == Error_types.WILL_BE_IMPORTED or error == Error_types.HAS_BEEN_IMPORTED:
                    output["error_msg"] = regex_matched.group(4) + " is reference item"
                elif error == Error_types.WILL_BE_IMPORTED or error == Error_types.HAS_BEEN_IMPORTED:
                    output["error_msg"] = regex_matched.group(3) + " is original bibblionumber"
                try:
                    item = OMEKA.get_resource_by_id(output["item_id"], "items")
                except requests.exceptions.RequestException as generic_error:
                    output = default_output_line(output)
                else:
                    try:
                        output["title"] = item["o:title"]
                        output["school"] = item["dcterms:provenance"][0]["@value"]
                    except:
                        output = default_output_line(output)
            else:
                output = default_output_line(output)
            CSV_WRITER.writerow(output)

# Close errors file
OUTPUT_FILE.close()
