import pandas as pd
from pathlib import Path
import math
import numpy as np
from scipy.spatial import cKDTree

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

file1 = base / "Cleaned_Data" / "iNat_cleaned_sheets" / "iNat_juglans_nigra_cleaned.csv"
file2 = base / "Cleaned_Data" / "GBIF_cleaned_sheets" / "gbif_juglans_nigra_cleaned.csv"

df1 = pd.read_csv(file1, dtype=str)
df2 = pd.read_csv(file2, dtype=str)

# Clean column names
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# Rename iNat columns to match GBIF columns
df1 = df1.rename(columns={
    'scientific_name': 'species',
    'latitude': 'decimalLatitude',
    'longitude': 'decimalLongitude',
    'observed_on_string': 'dateIdentified',
    'positional_accuracy': 'coordinateUncertaintyInMeters',
})

columns_to_keep = [
    'species',
    'decimalLatitude',
    'decimalLongitude',
    'dateIdentified',
    'coordinateUncertaintyInMeters'
]

df1 = df1[columns_to_keep].copy()
df2 = df2[columns_to_keep].copy()

# Stack vertically
combined = pd.concat([df1, df2], axis=0, ignore_index=True)

combined["Source"] = ["iNat"] * len(df1) + ["GBIF"] * len(df2)

print("Combined DataFrame length before cleaning:", len(combined))

# Convert numeric columns
combined["decimalLatitude"] = pd.to_numeric(combined["decimalLatitude"], errors="coerce") # means any non-convertible value will become NaN
combined["decimalLongitude"] = pd.to_numeric(combined["decimalLongitude"], errors="coerce")
combined["coordinateUncertaintyInMeters"] = pd.to_numeric(
    combined["coordinateUncertaintyInMeters"], errors="coerce"
)

# Remove rows with coarse rounding in coordinates (1 or fewer decimal places)
combined = combined[
    (combined['decimalLatitude'].astype(str).str.split('.').str[1].str.len() > 1) &
    (combined['decimalLongitude'].astype(str).str.split('.').str[1].str.len() > 1)
].reset_index(drop=True)

print("Combined length after phase 2 (quality filtering):", len(combined))

# Drop rows with missing coordinates just in case
combined = combined.dropna(subset=["decimalLatitude", "decimalLongitude"]).reset_index(drop=True)

# Sort so lower uncertainty comes first
combined = combined.sort_values(
    by="coordinateUncertaintyInMeters",
    ascending=True,
    na_position="last"
).reset_index(drop=True)

# Convert to radians for spatial indexing
coords_rad = np.radians(combined[['decimalLatitude', 'decimalLongitude']].values)

# Convert to 3D unit sphere coordinates for KDTree
x = np.sin(np.pi/2 - coords_rad[:, 0]) * np.cos(coords_rad[:, 1])
y = np.sin(np.pi/2 - coords_rad[:, 0]) * np.sin(coords_rad[:, 1])
z = np.cos(np.pi/2 - coords_rad[:, 0])
sphere_coords = np.column_stack([x, y, z])

# Build KDTree
tree = cKDTree(sphere_coords)

# Radius in chord distance: 100m / 6371000m Earth radius
# Chord distance = 2 * sin(angle/2)
radius = 2 * np.sin(100 / 6371000 / 2)

keep_indices = []
for i in range(len(combined)):
    # Query neighbors within radius
    neighbors = tree.query_ball_point(sphere_coords[i], radius)
    
    # Check if any neighbor is already in keep_indices
    is_close = any(neighbor in keep_indices for neighbor in neighbors if neighbor != i)
    
    if not is_close:
        keep_indices.append(i)

combined = combined.iloc[keep_indices].reset_index(drop=True)

print("Combined DataFrame length after phase 3 (removing exact/near duplicates within 100m):", len(combined))
print(combined.head())
print(combined.tail())

output_file = base / "Cleaned_Data" / "combined_juglans_nigra.csv"
combined.to_csv(output_file, index=False)

print(f"Combined data saved to: {output_file}")