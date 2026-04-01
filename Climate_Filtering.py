import pandas as pd
from pathlib import Path
import rasterio 

base = Path.home() / "OneDrive" / "Desktop" / "Research Project Spring 26'" / "Phase 1_ Data Cleaning"

input_file = base / "Cleaned_Data" / "Cleaning2and3" / "combined_vitus_vinifera.csv"
raster_file = base / "Climate_Data" / "wc2.1_30s_bio_1.tif"
output_file = base / "Cleaned_Data" / "vitus_vinifera_thinned.csv"

#read in file
df = pd.read_csv(input_file)

print("Number of records before raster thinning:", len(df))

# Confirm cords are numeric
df["decimalLatitude"] = pd.to_numeric(df["decimalLatitude"], errors="coerce")
df["decimalLongitude"] = pd.to_numeric(df["decimalLongitude"], errors="coerce")

# Confirm missed values are dropped
df = df.dropna(subset=["decimalLatitude", "decimalLongitude"]).reset_index(drop=True)

# Assigns each point to a raster cell 
with rasterio.open(raster_file) as src:
    print("Raster CRS:", src.crs)

    rows_cols = [
        src.index(lon, lat)
        for lon, lat in zip(df["decimalLongitude"], df["decimalLatitude"])
    ]

# Save raster row/col
df["raster_row"] = [rc[0] for rc in rows_cols]
df["raster_col"] = [rc[1] for rc in rows_cols]

# Keep one point per raster cell
df = df.drop_duplicates(subset=["raster_row", "raster_col"], keep="first").reset_index(drop=True)

print("Number of records after raster thinning:", len(df))

# Drop raster row/col as they are no longer needed
df = df.drop(columns=["raster_row", "raster_col"])

# Keep updated cleaned columns
final_cols = [col for col in ["species", "decimalLatitude", "decimalLongitude", "dateIdentified", "Source"] if col in df.columns]
df = df[final_cols]

# Save thinned data
df.to_csv(output_file, index=False)

print(f"Thinned data saved to: {output_file}")
print(df.head())