import pandas as pd
from pathlib import Path
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2)**2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2)**2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

base = Path.home() / "OneDrive" / "Desktop" / "Research Project Spring 26'" / "Phase 1_ Data Cleaning"

# Put one file or many files in this list
input_files = [
    ("GBIF", base / "Cleaned_Data" / "GBIF_cleaned_sheets" / "gbif_juglans_regia_cleaned.csv"),
    ("iNat", base / "Cleaned_Data" / "iNat_cleaned_sheets" / "iNat_juglans_regia_cleaned.csv")
]

columns_to_keep = [
    'species',
    'decimalLatitude',
    'decimalLongitude',
    'dateIdentified',
    'coordinateUncertaintyInMeters'
]

all_dfs = []

for source_name, file_path in input_files:
    df = pd.read_csv(file_path, dtype=str)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Rename iNat columns if needed
    df = df.rename(columns={
        'scientific_name': 'species',
        'latitude': 'decimalLatitude',
        'longitude': 'decimalLongitude',
        'observed_on_string': 'dateIdentified',
        'positional_accuracy': 'coordinateUncertaintyInMeters',
    })

    df = df[columns_to_keep].copy()
    df["Source"] = source_name

    all_dfs.append(df)

# Combine all files, even if there is only one
combined = pd.concat(all_dfs, axis=0, ignore_index=True)

print("Combined DataFrame length before cleaning:", len(combined))

# Convert numeric columns
combined["decimalLatitude"] = pd.to_numeric(combined["decimalLatitude"], errors="coerce")
combined["decimalLongitude"] = pd.to_numeric(combined["decimalLongitude"], errors="coerce")
combined["coordinateUncertaintyInMeters"] = pd.to_numeric(
    combined["coordinateUncertaintyInMeters"], errors="coerce"
)

# Drop rows with missing coordinates BEFORE coarse rounding check
combined = combined.dropna(subset=["decimalLatitude", "decimalLongitude"]).reset_index(drop=True)

# Remove rows with coarse rounding in coordinates
combined = combined[
    (combined['decimalLatitude'].astype(str).str.split('.').str[1].fillna('').str.len() > 1) &
    (combined['decimalLongitude'].astype(str).str.split('.').str[1].fillna('').str.len() > 1)
].reset_index(drop=True)

print("Combined length after phase 2 (quality filtering):", len(combined))

# Sort so lower uncertainty comes first
combined = combined.sort_values(
    by="coordinateUncertaintyInMeters",
    ascending=True,
    na_position="last"
).reset_index(drop=True)

keep_indices = []

for i in range(len(combined)):
    lat1 = combined.loc[i, "decimalLatitude"]
    lon1 = combined.loc[i, "decimalLongitude"]

    is_duplicate = False

    for kept_i in keep_indices:
        lat2 = combined.loc[kept_i, "decimalLatitude"]
        lon2 = combined.loc[kept_i, "decimalLongitude"]

        dist = haversine_distance(lat1, lon1, lat2, lon2)

        if dist <= 100:
            is_duplicate = True
            break

    if not is_duplicate:
        keep_indices.append(i)

combined = combined.iloc[keep_indices].reset_index(drop=True)

print("Combined DataFrame length after phase 3 (removing exact/near duplicates within 100m):", len(combined))
print(combined.head())
print(combined.tail())

output_file = base / "Cleaned_Data" / "combined_juglans_regia.csv"
combined.to_csv(output_file, index=False)

print(f"Combined data saved to: {output_file}")