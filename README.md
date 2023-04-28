# Omeka-S

Utilise : https://github.com/wragge/omeka_s_tools
Doc : https://wragge.github.io/omeka_s_tools/api.html

__omekas_s_tools v0.3.0 ne permet pas de GET des ressources privées via `.get_resource_by_id()`.__
Certains GET permettent de rajouter des `**kwargs`, donc je n'ai pas touché à ceux-là.

__ATTENTION__ : la version utilisée ici de [omeka_s_tools](https://github.com/wragge/omeka_s_tools) __est une fork__ permettant d'utiliser la fonction `.get_resource_by_id()` sur des ressources privées ([voir comment l'installer](#installer-la-fork-domeka_s_tools)).

# Fichiers

* [Corriger les problèmes de visibilité (de contenus et médias)](./fix_visibility_issues.py) :
  * Basé sur l'utilisation [du module Group](https://github.com/Daniel-KM/Omeka-S-module-Group)
  * Part du principe que la visibilité d'un document n'est restreint qu'au niveau du média, pas du contenu (sauf si le contenu est en cours de traitement)
  * Deux traitements :
    * l'attribution des groupes du contenu aux médias liés, le passage des médias en privé, la suppression des groupes du contenu, la passage du contenu en public
    * la suppression des groupes du contenu, la passage du contenu en public

## Upload medias to items via biblionumber

_[Link to the file](./upload_medias_to_items_via_bibnb.py)_

A script that uploads and attaches files to items in Omeka S.
Uses Koha biblionumber to ensure that the targeted item is the correct one.
If groups are provided, the uploaded media will be private with these groups assigned, otherwise the media will be public.

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
* `OUTPUT_FOLDER` : folder where output files will be created
* `OMEKA_URL` : URL of Omeka S
* `OMEKA_KEY_IDENTITY` : Omeka S API key identity
* `OMEKA_KEY_CREDENTIAL` : Omeka S API key credential

### File with data

* Must be readable by `pandas.read_excel()`
* Three columns are required (with these names) :
  * `file_name` : name of the file (with extension, not the full path)
  * `bibnb` : Koha biblionumber of the record
  * `id_item` : Omeka S ID of the item

### Information that will be asked in the terminal

* Full path to the file with data
* Full path to the folder containing the files
* Omeka-S groups ID to add
  * Groups must be separated by a comma
  * All groups that throws an exception on `int(group.strip())` are ignored

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