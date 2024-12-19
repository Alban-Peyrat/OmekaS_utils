# Omeka-S

* Uses : https://github.com/wragge/omeka_s_tools
* Documentation : https://wragge.github.io/omeka_s_tools/api.html
* __omekas_s_tools v0.3.0 does not allow `GET` on private resources using `.get_resource_by_id()`.__
  * Some `GET` allow the use of `**kwargs`, so I did not edit them
* __/!\\__ : the version used in this repository of [omeka_s_tools](https://github.com/wragge/omeka_s_tools) __is a fork__ allowing the use of `.get_resource_by_id()` on private resources ([see How to install](#installer-la-fork-domeka_s_tools)).

# Scripts

## Fix visibility issues

_[Link to the file](./fix_visibility_issues.py)_

A script that updates visibilty properties of items and/or medias.
Assumes that __items are always public__ (unless they are ebing processed, but the script should not be used on them) and only medias can have a restricted access.
Current possible jobs :

* __0__ : Spread item visibility to medias _(untested on items without groups)_
  * Gets the item groups
  * Forces the attached medias to be private
  * Forces the attached medias to have the item's groups
  * Forces the item groups to be empty
  * Forces the item to be public
* __1__ : Clean item visibility
  * Forces the item groups to be empty
  * Forces the item to be public
* __9__ : Add groups to medias by item id
  * Gets the attached media groups
  * Forces the attached media to be private
  * Adds the specified groups to the groups of the media

The service name (used to name the log file) is : *Omeka-S_-_Fix_visibility_issues*

### Omeka S modules used

* [Group (module for Omeka S)](https://github.com/Daniel-KM/Omeka-S-module-Group)

### Libraries used

* Python Standard Library
  * [json](https://docs.python.org/3/library/json.html)
  * [logging](https://docs.python.org/3/library/logging.html)
  * [os](https://docs.python.org/3/library/os.html)
* External libraries
  * [python-dotenv](https://pypi.org/project/python-dotenv/)
  * [Omeka S Tools](https://pypi.org/project/omeka-s-tools/) __/!\\ If some of items are private, v0.3.0 won't find them.__ I use [my own fork](https://github.com/Alban-Peyrat/omeka_s_tools) (forces `.get_resource_by_id()` to provide the API key)
  * [Requests](https://pypi.org/project/requests/)
* Internal files
  * [logs.py](https://github.com/louxfaure/logs/tree/master) by Alexandre Faure (@louxfaure), with an additional parameter `encoding='utf-8'` to `RotatingFileHandler()`
  * [archires_coding_convention_resources.py] : a set of functions by ArchiRès, the file is provided in this repository

### Required environment variables

_Paths (URL or folders) should not have trailing `/`_

* `LOGS_FOLDER` : full path to the folder where the log file will be created
* `LOGGER_LEVEL` : optionnal, must be equel to `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. If omitted or not in this list, is set to `INFO`
* `INPUT_FILE_FIX_VISIBILITY` : full path to the file with data : just a list of Omeka-S ids separated by newlines with no header
* `OUTPUT_FOLDER` : folder where output files will be created
* `OMEKA_URL` : URL of Omeka S
* `OMEKA_KEY_IDENTITY` : Omeka S API key identity
* `OMEKA_KEY_CREDENTIAL` : Omeka S API key credential

### Information that will be asked in the terminal

* Which job should be executed
* Omeka-S groups ID to add
  * Groups must be separated by a comma
  * All groups that throws an exception on `int(group.strip())` are ignored

### Output files

* `errors.csv` : the file containing errors, with 4 columns :
  * `index` : index of the row in the file with data
  * `provided_omeka_id` : the ID provided in the file with data
  * `resource` : if known, which Omeka-S ressource is concerned, if unknown : `unknown`
  * `error` : the error message
* `item_get.json` : a JSON containing an array of all the items that succesfully were retrieved through the `GET`
* `item_post.json` : a JSON containing an array of all the items that were returned by successfull `POST`
* `media_get.json` : a JSON containing an array of all the medias that succesfully were retrieved through the `GET`
* `media_post.json` : a JSON containing an array of all the medias that were returned by successfull `POST`

## Upload medias to items via biblionumber

_[Link to the file](./upload_medias_to_items_via_bibnb.py)_

A script that uploads and attaches files to items in Omeka S.
Uses Koha biblionumber to ensure that the targeted item is the correct one.
If groups are provided, the uploaded media will be private with these groups assigned, otherwise the media will be public.

The service name (used to name the log file) is : *Omeka-S_-_Upload_medias_to_items_via_bibnb*

### Omeka S modules used

* [Group (module for Omeka S)](https://github.com/Daniel-KM/Omeka-S-module-Group)
* [Biblionumber Support for Omeka S](https://github.com/biblibre/omeka-s-module-BiblionumberSupport)

### Libraries used

* Python Standard Library
  * [json](https://docs.python.org/3/library/json.html)
  * [logging](https://docs.python.org/3/library/logging.html)
  * [os](https://docs.python.org/3/library/os.html)
* External libraries
  * [python-dotenv](https://pypi.org/project/python-dotenv/)
  * [Omeka S Tools](https://pypi.org/project/omeka-s-tools/) __/!\\ If some of items are private, v0.3.0 won't find them.__ I use [my own fork](https://github.com/Alban-Peyrat/omeka_s_tools) (forces `.get_resource_by_id()` to provide the API key)
  * [pandas](https://pypi.org/project/pandas/) (might need additional engine depending on the file format used)
  * [Requests](https://pypi.org/project/requests/)
* Internal files
  * [logs.py](https://github.com/louxfaure/logs/tree/master) by Alexandre Faure (@louxfaure), with an additional parameter `encoding='utf-8'` to `RotatingFileHandler()`

### Required environment variables

_Paths (URL or folders) should not have trailing `/`_

* `LOGS_FOLDER` : full path to the folder where the log file will be created
* `INPUT_FILE_MEDIA_LIST` : full path to the file with data
* ~~`UPLOAD_FILES_FROM_FTP` : upload files from a FTP server ? `1` if yes, `0` or can be omitted if no~~
* `FILES_FOLDER` : full path to the folder containing the files. Can be omitted if `UPLOAD_FILES_FROM_FTP` is set to `1`.
* `OUTPUT_FOLDER` : folder where output files will be created
* `OMEKA_URL` : URL of Omeka S
* `OMEKA_KEY_IDENTITY` : Omeka S API key identity
* `OMEKA_KEY_CREDENTIAL` : Omeka S API key credential
* `LOGGER_LEVEL` : optionnal, must be equel to `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. If omitted or not in this list, is set to `INFO`

### File with data

* Must be readable by `pandas.read_excel()`, unless the file format is `.csv` (separator must be `;`)
* Three columns are required (with these names) :
  * `file_name` : name of the file (with extension, not the full path)
  * `bibnb` : Koha biblionumber of the record
  * `id_item` : Omeka S ID of the item

### Information that will be asked in the terminal

* Omeka-S groups ID to add
  * Groups must be separated by a comma
  * All groups that throws an exception on `int(group.strip())` are ignored

## Normalize `importJob` log errors (from `EnsaKohaImport`)

_[Link to the file](./normalize_importJob_log_errors.py)_

A script that changes logs from this job to a spreadsheet with the school, to handle a big number of errors.

### Omeka S modules used

* [Biblionumber Support for Omeka S](https://github.com/biblibre/omeka-s-module-BiblionumberSupport)
* Ensa Koha Import

### Libraries used

* Python Standard Library
  * [os](https://docs.python.org/3/library/os.html)
  * [csv](https://docs.python.org/3/library/csv.html)
  * [enum](https://docs.python.org/3/library/enum.html)
  * [re](https://docs.python.org/3/library/re.html)
* External libraries
  * [python-dotenv](https://pypi.org/project/python-dotenv/)
  * [Omeka S Tools](https://pypi.org/project/omeka-s-tools/) __/!\\ If some of items are private, v0.3.0 won't find them.__ I use [my own fork](https://github.com/Alban-Peyrat/omeka_s_tools) (forces `.get_resource_by_id()` to provide the API key)
  * [Requests](https://pypi.org/project/requests/)
* Internal files
  * [archires_coding_convention_resources.py] : a set of functions by ArchiRès, the file is provided in this repository
  * [Koha_API_PublicBiblio.py] : a set of function to use Koha public biblio API (2024 june 10 version)

### Required environment variables

_Paths (URL or folders) should not have trailing `/`_

* `NIJLE_INPUT_FILE` : full path to the file with data (a copy paste of the logs)
* `OUTPUT_FOLDER` : folder where output file will be created
* `OMEKA_URL` : URL of Omeka S
* `OMEKA_KEY_IDENTITY` : Omeka S API key identity
* `OMEKA_KEY_CREDENTIAL` : Omeka S API key credential
* `KOHA_URL` : URL of Koha

### Output file

A csv file containing 6 columns :

  * `item_id` : Omeka-S item ID that triggererd the error
  * `bibnb` : the bibnb of this item
  * `error` : the error name
  * `error_msg` : the error message. If an ID is provided inside, it will always be the beginning of the message
  * `school` : the school that uplaoded the media (first dublin core provenance, for older items, might not be the expected value)
  * `title` : the title of the item in Omeka-S
  * `media` : does the item contain medias in Omeka-S ?
  * `item_sets` : all item sets label for which this item is a part of
  * `koha_record` : does Koha still have a record for this biblionumber
  * `koha_export_omeka` : value of the `099$x` in the Koha record (`no 099$x` if there is no `099$x`, emty if no Koha record was found)

If data could not be retrieved, will always write `err` instead of a value

# Informations importantes

* Pour rajouter des groupes, à partir d'un GET __stringifier les `o:id`__

## Attacher un media à un item

Ce bout de code permet de rattacher un média depuis mon ordinateur au contenu `68356`, en spécifiant :

* que le média est privé
* que le média n'est accessible qu'aux adminstratifs de Bordeaux (`3325`)

La fonction `add_media_toitem()` renvoie l'objet sous forme de dictionnaire.

```Python
# Init the class
omeka = OmekaAPIClient(omeka_url + "/api", key_identity=key_identity, key_credential=key_credential)

# Adding metadata
payload = {
    "o:is_public":False,
    "o-module-group:group":[{"o:id":"3325"}]
}

# Add a new media file with a metadata payload to the item
a = omeka.add_media_to_item(68356, r"C:\File\To\path.pdf", payload=payload)
```

## Modifier un media existant

``` Python
media = OmekaS_API(omeka_url=omeka_url, api="media", HTTPmethod="GET", id="68385", key_identity=key_identity, key_credential=key_credential)
media["o:is_public"] = False
media["o-module-group:group"] = [{"o:id":"3325"}]
media_updated = omeka.update_resource(media, "media")
```

## Récupérer l'id de l'item correspondant à un biblionumber Koha

|| à faire

## Supprimer des médias

``` Python
for resource_id in id_list:
    r = requests.delete("{}/api/{}/{}?key_identity={}&key_credential={}".format(
        str(omeka_url), str(api_resource), str(resource_id), str(key_identity), str(key_credential)
    ))
    print(resource_id)
    print(r.status_code)

    deleted_items.append(r.content.decode('utf-8'))

with open(output_path, mode="w", encoding="utf-8") as f:
    json.dump(deleted_items, f, ensure_ascii=False, indent=4)
```

# Installer la fork d'omeka_s_tools

1. Si omeka_s_tools est déjà installé, le désinstallé : `pip uninstall omeka_s_tools`
1. Cloner sur l'ordinateur [mon fork](https://github.com/Alban-Peyrat/omeka_s_tools)
1. Dans l'invite de commande, naviguer jusqu'au dossier (via `cd`)
1. Exécuter la commande `pip install .`