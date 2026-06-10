import pandas as pd


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
    "Art": "Art",
    "Træk": "Træk",
    "Drivmiddel": "Drivmiddel",
    "Reg. nr.": "Reg. nr.",
    "Mærke": "Mærke",
    "Model": "Model",
    "Anvendelse": "Anvendelse",
    "Stel nr. ": "Stel nr. "
}


ACTIVE_DEFAULT_DATE = pd.Timestamp("1900-01-01")


def is_active_vehicle(afg_dato):
    if pd.isna(afg_dato) or afg_dato == "":
        return True

    dt = pd.to_datetime(afg_dato, errors="coerce")
    if pd.isna(dt):
        return False

    return dt.tz_localize(None).normalize() == ACTIVE_DEFAULT_DATE if getattr(dt, "tzinfo", None) else dt.normalize() == ACTIVE_DEFAULT_DATE
