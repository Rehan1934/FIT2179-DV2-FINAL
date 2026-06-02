from pathlib import Path
import json
from collections import Counter

input_path = Path("data/processed/world_countries.geojson")
output_path = Path("data/processed/asean_map_final.geojson")

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

def clean_text(value):
    return str(value).strip().lower()

def find_country(feature):
    props = feature.get("properties", {})

    # First try ISO-style values
    candidates = [feature.get("id")]
    candidates.extend(props.values())

    for value in candidates:
        if value is None:
            continue

        value_str = str(value).strip()
        value_upper = value_str.upper()

        if value_upper in ASEAN:
            return value_upper

        value_clean = clean_text(value_str)
        if value_clean in NAME_TO_ISO:
            return NAME_TO_ISO[value_clean]

    return None

data = json.loads(input_path.read_text(encoding="utf-8"))

clean_features = []

for feature in data["features"]:
    iso = find_country(feature)

    if iso not in ASEAN:
        continue

    info = ASEAN[iso]

    feature["properties"] = {
        "iso": iso,
        "country": info["country"],
        "depression": info["depression"],
        "anxiety": info["anxiety"],
        "group": info["group"]
    }

    clean_features.append(feature)

clean_data = {
    "type": "FeatureCollection",
    "features": clean_features
}

output_path.write_text(json.dumps(clean_data), encoding="utf-8")

countries_found = Counter(f["properties"]["country"] for f in clean_features)
print("Saved:", output_path)
print("Countries found:", countries_found)

missing = set(v["country"] for v in ASEAN.values()) - set(countries_found.keys())

if missing:
    print("MISSING:", sorted(missing))
else:
    print("SUCCESS: All ASEAN countries found.")
