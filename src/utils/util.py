
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
