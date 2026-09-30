# -*- coding: utf-8 -*-
"""Chaines de l'interface 237Boots (francais par defaut, anglais en secours).

Deux locales sont fournies : fr_CM (francais - Cameroun, defaut) et
en_CM (anglais - Cameroun). Le choix est fige a la compilation du paquetage
pour eviter toute dependance a une locale Windows absente.
"""

from __future__ import annotations

FR = {
    "app_title": "237Boots",
    "app_subtitle": "Creer une cle USB amorcable",
    "lang": "Langue",
    "devices": "Disques",
    "refresh": "Actualiser",
    "no_device": "Aucun disque detecte.",
    "disk": "Disque {index}",
    "size": "Taille",
    "scheme": "Table",
    "bus": "Bus",
    "generic_model": "Modele inconnu",
    "removable": "Amovible",
    "external": "Externe",
    "system_disk": "Disque systeme",
    "boots_installed": "237Boots installe",
    "options": "Options",
    "partition_style": "Style de partition",
    "gpt": "GPT (recommandé)",
    "mbr": "MBR (compatibilite ancienne)",
    "secure_boot": "Activer Secure Boot (UEFI)",
    "secure_boot_hint": "Necessite l'enrolement de la cle 237Boots dans MokManager.",
    "ignore_usb_check": "Ignorer la verification USB",
    "actions": "Actions",
    "install": "Installer",
    "update": "Mettre a jour",
    "erase": "Effacer",
    "cancel": "Annuler",
    "close": "Fermer",
    "confirm_title": "Confirmation",
    "confirm_install": (
        " toutes les donnees du disque {name} seront effacees.\n\n"
        "Cette operation est irreversible. Voulez-vous continuer ?"
    ),
    "confirm_erase": "Confirmer l'effacement du disque {name} ?",
    "no_selection": "Selectionnez d'abord un disque.",
    "progress": "Progression",
    "ready": "Pret",
    "working": "Operation en cours...",
    "log": "Journal",
    "clear_log": "Vider",
    "help": "Aide",
    "docs": "Documentation",
    "github": "Depot GitHub",
    "about": "A propos",
    "about_text": (
        "<b>237Boots</b> {version}<br/>"
        "Version camerounaise de Ventoy.<br/><br/>"
        "Fork de <a href='https://github.com/ventoy/Ventoy'>Ventoy</a> "
        "de longpanda, sous licence GPL v3+.<br/>"
        "Auteur : Edmond Noumegni."
    ),
    "engine_missing": (
        "Moteur introuvable (Ventoy2Disk.exe). Placez-le a cote de 237Boots.exe."
    ),
    "done": "Termine",
    "failed": "Echec",
}

EN = {
    "app_title": "237Boots",
    "app_subtitle": "Create a bootable USB drive",
    "lang": "Language",
    "devices": "Disks",
    "refresh": "Refresh",
    "no_device": "No disk detected.",
    "disk": "Disk {index}",
    "size": "Size",
    "scheme": "Scheme",
    "bus": "Bus",
    "generic_model": "Unknown model",
    "removable": "Removable",
    "external": "External",
    "system_disk": "System disk",
    "boots_installed": "237Boots installed",
    "options": "Options",
    "partition_style": "Partition style",
    "gpt": "GPT (recommended)",
    "mbr": "MBR (legacy compatibility)",
    "secure_boot": "Enable Secure Boot (UEFI)",
    "secure_boot_hint": "Requires enrolling the 237Boots key in MokManager.",
    "ignore_usb_check": "Ignore USB check",
    "actions": "Actions",
    "install": "Install",
    "update": "Update",
    "erase": "Erase",
    "cancel": "Cancel",
    "close": "Close",
    "confirm_title": "Confirmation",
    "confirm_install": (
        " all data on disk {name} will be erased.\n\n"
        "This operation is irreversible. Do you want to continue?"
    ),
    "confirm_erase": "Confirm erasing disk {name}?",
    "no_selection": "Select a disk first.",
    "progress": "Progress",
    "ready": "Ready",
    "working": "Operation in progress...",
    "log": "Log",
    "clear_log": "Clear",
    "help": "Help",
    "docs": "Documentation",
    "github": "GitHub repository",
    "about": "About",
    "about_text": (
        "<b>237Boots</b> {version}<br/>"
        "Cameroon edition of Ventoy.<br/><br/>"
        "Fork of <a href='https://github.com/ventoy/Ventoy'>Ventoy</a> "
        "by longpanda, licensed under GPL v3+.<br/>"
        "Author: Edmond Noumegni."
    ),
    "engine_missing": (
        "Engine not found (Ventoy2Disk.exe). Place it next to 237Boots.exe."
    ),
    "done": "Done",
    "failed": "Failed",
}

# locale -> table. fr_CM est l'identifiant de localettemberg de l'edition
# camerounaise ; on garde aussi les alias usuels.
TABLES = {"fr_CM": FR, "fr_FR": FR, "en_CM": EN, "en_US": EN}
DEFAULT = "fr_CM"

_current = DEFAULT


def set_locale(name: str) -> None:
    global _current
    _current = name if name in TABLES else DEFAULT


def get_locale() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    table = TABLES.get(_current, FR)
    value = table.get(key, FR.get(key, key))
    return value.format(**kwargs) if kwargs else value
