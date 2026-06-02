from pathlib import Path
import json
from collections import Counter

input_path = Path("data/processed/world_countries.geojson")
output_path = Path("data/processed/asean_countries_mental.geojson")

ASEAN = {
    "MYS": {"country": "Malaysia", "depression": 3.52, "anxiety": 4.34, "group": "Malaysia"},
    "SGP": {"country": "Singapore", "depression": 3.44, "anxiety": 3.73, "group": "Other ASEAN countries"},
    "THA": {"country": "Thailand", "depression": 3.09, "anxiety": 3.33, "group": "Other ASEAN countries"},
    "KHM": {"country": "Cambodia", "depression": 3.09, "anxiety": 3.29, "group": "Other ASEAN countries"},
    "LAO": {"country": "Laos", "depression": 2.91, "anxiety": 4.22, "group": "Other ASEAN countries"},
    "VNM": {"country": "Vietnam", "depression": 2.88, "anxiety": 2.07, "group": "Other ASEAN countries"},
    "PHL": {"country": "Philippines", "depression": 2.77, "anxiety": 3.27, "group": "Other ASEAN countries"},
    "IDN": {"country": "Indonesia", "depression": 2.64, "anxiety": 3.28, "group": "Other ASEAN countries"},
    "BRN": {"country": "Brunei", "depression": 2.56, "anxiety": 3.62, "group": "Other ASEAN countries"},
    "MMR": {"country": "Myanmar", "depression": 2.30, "anxiety": 3.31, "group": "Other ASEAN countries"},
}

NAME_TO_ISO = {
    "malaysia": "MYS",
    "singapore": "SGP",
    "thailand": "THA",
    "cambodia": "KHM",
    "laos": "LAO",
    "lao pdr": "LAO",
    "lao people's democratic republic": "LAO",
    "vietnam": "VNM",
    "viet nam": "VNM",
    "philippines": "PHL",
    "indonesia": "IDN",
    "brunei": "BRN",
    "brunei darussalam": "BRN",
    "myanmar": "MMR",
    "burma": "MMR",
}

def find_iso(feature):
    props = feature.get("properties", {})
    candidates = [
        feature.get("id"),
        props.get("ISO_A3"),
        props.get("ADM0_A3"),
        props.get("WB_A3"),
        props.get("iso_a3"),
        props.get("adm0_a3"),
        props.get("ISO3166-1-Alpha-3"),
        props.get("ISO3166_1_Alpha_3"),
    ]

    for value in candidates:
        if value and str(value).upper() in ASEAN:
            return str(value).upper()

    name_candidates = [
        props.get("name"),
        props.get("NAME"),
        props.get("ADMIN"),
        props.get("admin"),
        props.get("country"),
        props.get("Country"),
    ]

    for value in name_candidates:
        if value:
            key = str(value).strip().lower()
            if key in NAME_TO_ISO:
                return NAME_TO_ISO[key]

    return None

data = json.loads(input_path.read_text(encoding="utf-8"))

clean_features = []

for feature in data["features"]:
    iso = find_iso(feature)

    if iso not in ASEAN:
        continue

    info = ASEAN[iso]

    feature["properties"]["iso"] = iso
    feature["properties"]["country"] = info["country"]
    feature["properties"]["depression"] = info["depression"]
    feature["properties"]["anxiety"] = info["anxiety"]
    feature["properties"]["group"] = info["group"]

    clean_features.append(feature)

clean_data = {
    "type": "FeatureCollection",
    "features": clean_features
}

output_path.write_text(json.dumps(clean_data), encoding="utf-8")

print("Saved:", output_path)
print("Number of ASEAN country features:", len(clean_features))
print("Country counts:", Counter(f["properties"]["country"] for f in clean_features))

missing = set(info["country"] for info in ASEAN.values()) - set(f["properties"]["country"] for f in clean_features)
if missing:
    print("MISSING:", sorted(missing))
else:
    print("All ASEAN countries found.")
