# Omeka-S

Utilise : https://github.com/wragge/omeka_s_tools
Doc : https://wragge.github.io/omeka_s_tools/api.html

__omekas_s_tools v0.3.0 ne permet pas de GET des ressources privées via `.get_resource_by_id()`.__
Certains GET permettent de rajouter des `**kwargs`, 

__ATTENTION__ : la version utilisée ici de [omeka_s_tools](https://github.com/wragge/omeka_s_tools) __est une fork__ permettant d'utiliser la fonction `.get_resource_by_id()` sur des ressources privées ([voir comment l'installer](#installer-la-fork-domeka_s_tools)).

# Fichiers

* [Corriger les problèmes de visibilité (de contenus et médias)](./fix_visibility_issues.py) :
  * Basé sur l'utilisation [du module Group](https://github.com/Daniel-KM/Omeka-S-module-Group)
  * Part du principe que la visibilité d'un document n'est restreint qu'au niveau du média, pas du contenu (sauf si le contenu est en cours de traitement)
  * 

# Informations importantes

* Pour rajouter des groupes, à partir d'un GET __seulement indiquer les `o:id`__, pas les autres informations

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