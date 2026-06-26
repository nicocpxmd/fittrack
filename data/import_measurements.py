import pandas as pd
import json
from datetime import datetime

INPUT_FILE = "body measurements.xlsx"
OUTPUT_FILE = "measurements.json"

COLUMN_MAP = {
    "Weight":    "weight_kg",
    "Height":    "height_cm",
    "Neck":      "neck_cm",
    "Shoulder":  "shoulder_cm",
    "Chest":     "chest_cm",
    "Arm":       "arm_cm",
    "Forearm":   "forearm_cm",
    "Waist":     "waist_cm",
    "Abdomen":   "abdomen_cm",
    "Hip":       "hip_cm",
    "Upper Leg": "upper_leg_cm",
    "Lower Leg": "lower_leg_cm",
    "Calf":      "calf_cm",
}

def parse_date(col):
    """Parse date column header. Returns (iso_date, confidence)."""
    parts = str(col).strip().split("/")
    if len(parts) == 1:
        return f"{parts[0]}-07-01", "year_only"
    elif len(parts) == 2:
        month, year = int(parts[0]), int(parts[1])
        return f"{year}-{month:02d}-01", "month_only"
    elif len(parts) == 3:
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{year}-{month:02d}-{day:02d}", "exact"
    return None, "unknown"

def get_context(iso_date):
    year = int(iso_date[:4])
    if year <= 2024:
        return "adolescent_growth"
    elif year == 2025:
        return "transition"
    return "adult_baseline"

def main():
    df = pd.read_excel(INPUT_FILE)

    # Normalize columns
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={"Concept": "concept", "Unit": "unit"})
    df = df[df["concept"].isin(COLUMN_MAP.keys())]
    df["field"] = df["concept"].map(COLUMN_MAP)

    date_cols = [c for c in df.columns if c not in ("concept", "unit", "field")]

    records = []
    for col in date_cols:
        iso_date, confidence = parse_date(col)
        if not iso_date:
            print(f"⚠️  Skipping unreadable column: {col}")
            continue

        measurements = {}
        for _, row in df.iterrows():
            val = row[col]
            if pd.notna(val):
                measurements[row["field"]] = float(val)

        record = {
            "date": iso_date,
            "date_confidence": confidence,
            "data_context": get_context(iso_date),
            "measurements": measurements,
            "notes": ""
        }
        records.append(record)
        print(f"✅ {iso_date} ({confidence}) — {len(measurements)} fields")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(records)} records saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()