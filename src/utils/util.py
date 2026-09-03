import re
import pandas as pd

# Danish license plates: 2 letters + 2-5 digits (e.g., AB12345), optionally with a space
REGNR_PATTERN = re.compile(r"^[A-ZÆØÅ]{2}\s?\d{2,5}$")


def is_valid_regnr(regnr):
    if not regnr or not isinstance(regnr, str):
        return False
    return bool(REGNR_PATTERN.match(regnr.strip().upper()))


def get_traek_icon(traek):
    icons = {
        "True": "✅",
        "False": "❌",
    }
    return icons.get(str(traek), "❓")


def get_drivmiddel_icon(drivmiddel):
    icons = {
        "El": "⚡",
        "Benzin": "⛽",
        "Diesel": "🛢️",
        "Ukendt": "❓",
    }
    icon = icons.get(drivmiddel, "🚗")
    return f"{icon} {drivmiddel}"


def get_most_specific_level(row):
    for level in ["Level_5", "Level_4", "Level_3", "Level_2", "Level_1"]:
        value = row.get(level)
        if pd.notna(value) and value != "":
            return f" {value}"
    return "Ingen hierarki angivet"


level_1_display_map = {
    "Børn & Skole": "Børn & Skole",
    "Miljø og Teknik": "Udvikling, Miljø & Teknik",
    "Randers Kommune": "Ukendt tilhørsforhold",
    "Social og arbejdsmarked": "Social & Arbejdsmarked",
    "Stabene": "Stabene",
    "Sundhed, kultur og omsorg": "Sundhed, Kultur & Omsorg",
}

export_columns_display_map = {
    "Level_1": "Forvaltning",
    "Level_2": "Level_2",
    "Level_3": "Level_3",
    "Level_4": "Level_4",
    "Level_5": "Level_5",
    "Level_6": "Level_6",
    "Status": "Status",
    "Reg. nr.": "Reg. nr.",
    "Årgang": "Årgang",
    "Reg.dato": "Reg.dato",
    "Afg.dato": "Afg.dato",
    "Stel nr. ": "Stel nr. ",
    "Art": "Art",
    "Træk": "Træk",
    "Drivmiddel": "Drivmiddel",
    "Mærke": "Mærke",
    "Model": "Model",
    "Anvendelse": "Anvendelse",
}


ACTIVE_DEFAULT_DATE = pd.Timestamp("1900-01-01")


def is_active_vehicle(afg_dato):
    if pd.isna(afg_dato) or afg_dato == "":
        return True

    dt = pd.to_datetime(afg_dato, errors="coerce")
    if pd.isna(dt):
        return False

    return dt.tz_localize(None).normalize() == ACTIVE_DEFAULT_DATE if getattr(dt, "tzinfo", None) else dt.normalize() == ACTIVE_DEFAULT_DATE
