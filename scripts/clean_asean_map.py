from pathlib import Path
import json
from collections import Counter

input_path = Path("data/processed/southeast-asia.geojson")
output_path = Path("data/processed/asean_mental_health_map.geojson")

MENTAL = {
    "Malaysia": {"depression": 3.52, "anxiety": 4.34, "group": "Malaysia"},
    "Singapore": {"depression": 3.44, "anxiety": 3.73, "group": "Other ASEAN countries"},
    "Thailand": {"depression": 3.09, "anxiety": 3.33, "group": "Other ASEAN countries"},
    "Cambodia": {"depression": 3.09, "anxiety": 3.29, "group": "Other ASEAN countries"},
    "Laos": {"depression": 2.91, "anxiety": 4.22, "group": "Other ASEAN countries"},
    "Vietnam": {"depression": 2.88, "anxiety": 2.07, "group": "Other ASEAN countries"},
    "Philippines": {"depression": 2.77, "anxiety": 3.27, "group": "Other ASEAN countries"},
    "Indonesia": {"depression": 2.64, "anxiety": 3.28, "group": "Other ASEAN countries"},
    "Brunei": {"depression": 2.56, "anxiety": 3.62, "group": "Other ASEAN countries"},
    "Myanmar": {"depression": 2.30, "anxiety": 3.31, "group": "Other ASEAN countries"},
}

def collect_points(coords, points):
    if isinstance(coords, list):
        if len(coords) >= 2 and isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
            lon, lat = coords[0], coords[1]
            if -180 <= lon <= 180 and -90 <= lat <= 90:
                points.append((lon, lat))
        else:
            for item in coords:
                collect_points(item, points)

def centroid(feature):
    points = []
    collect_points(feature.get("geometry", {}).get("coordinates", []), points)
    if not points:
        return None, None
    lon = sum(p[0] for p in points) / len(points)
    lat = sum(p[1] for p in points) / len(points)
    return lon, lat

def guess_country(lon, lat):
    # Small/specific places first
    if 103.3 <= lon <= 104.4 and 0.8 <= lat <= 1.8:
        return "Singapore"
    if 113.5 <= lon <= 116.5 and 3.5 <= lat <= 5.8:
        return "Brunei"

    # Malaysia before Indonesia because East Malaysia is on Borneo
    if 99 <= lon <= 120 and 0 <= lat <= 7.5:
        return "Malaysia"

    if 116 <= lon <= 127 and 4 <= lat <= 21:
        return "Philippines"
    if 94 <= lon <= 101 and 8 <= lat <= 28:
        return "Myanmar"
    if 100 <= lon <= 108 and 14 <= lat <= 23:
        return "Laos"
    if 97 <= lon <= 106 and 5 <= lat <= 19:
        return "Thailand"
    if 102 <= lon <= 108 and 9 <= lat <= 14:
        return "Cambodia"
    if 105 <= lon <= 111 and 8 <= lat <= 23:
        return "Vietnam"
    if 94 <= lon <= 141 and -11 <= lat <= 6:
        return "Indonesia"

    return None

data = json.loads(input_path.read_text(encoding="utf-8"))

clean_features = []
for feature in data["features"]:
    lon, lat = centroid(feature)
    country = guess_country(lon, lat)

    if country is None:
        continue

    feature["properties"]["country"] = country
    feature["properties"]["depression"] = MENTAL[country]["depression"]
    feature["properties"]["anxiety"] = MENTAL[country]["anxiety"]
    feature["properties"]["group"] = MENTAL[country]["group"]

    clean_features.append(feature)

clean_data = {
    "type": "FeatureCollection",
    "features": clean_features
}

output_path.write_text(json.dumps(clean_data), encoding="utf-8")

print("Saved", output_path)
print("Features:", len(clean_features))
print("Country counts:", Counter(f["properties"]["country"] for f in clean_features))
