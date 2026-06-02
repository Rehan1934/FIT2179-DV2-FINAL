from pathlib import Path
import json

files = [
    "specs/04_treatment_gap.json",
    "specs/07_cgpa_lollipop.json",
    "specs/14_pressure_profile.json"
]

def fix_x_value(obj):
    if isinstance(obj, dict):
        if "x" in obj and isinstance(obj["x"], dict) and obj["x"].get("value") == 0:
            obj["x"] = {"datum": 0}

        for value in obj.values():
            fix_x_value(value)

    elif isinstance(obj, list):
        for item in obj:
            fix_x_value(item)

for file in files:
    path = Path(file)

    if not path.exists():
        print(f"Missing: {file}")
        continue

    spec = json.loads(path.read_text(encoding="utf-8"))
    fix_x_value(spec)
    path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"Patched: {file}")

# Also patch the build script so rerunning it will not recreate the same issue.
build_script = Path("scripts/build_final_project.py")
if build_script.exists():
    text = build_script.read_text(encoding="utf-8")
    text = text.replace('"x": {"value": 0}', '"x": {"datum": 0}')
    build_script.write_text(text, encoding="utf-8")
    print("Patched: scripts/build_final_project.py")

print("Patch complete.")
