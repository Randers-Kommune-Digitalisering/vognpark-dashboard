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
