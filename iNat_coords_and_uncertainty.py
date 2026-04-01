from pathlib import Path
import pandas as pd

base = Path.home() / "OneDrive" / "Desktop" / "Research Project Spring 26'" / "Phase 1_ Data Cleaning"
file = base / "Raw_Data" / "SpottedLF_hosts" / "Vitis Vinifera" / "iNat_vitis_vinifera_raw.xlsx"

df = pd.read_excel(file, dtype=str)
print(df.head())

columns_to_keep = ['scientific_name', 'latitude', 'longitude','observed_on_string', 'positional_accuracy']
df = df[columns_to_keep]

print("DataFrame after keeping selected columns:")
print(df.head())

print("Rows before:", len(df))

# Cleaning missing longitude and latitude values
df = df.dropna(subset=['latitude', 'longitude'])
df = df[(df['latitude'] != '') & (df['longitude'] != '')]

print("Rows after cleaning coordinates:", len(df))

df["positional_accuracy"] = pd.to_numeric(
    df["positional_accuracy"], errors="coerce")

# Filter out high coordinate uncertainty
df = df[df['positional_accuracy'] < 1000]

print("Rows after filtering coordinate uncertainty < 1000:", len(df))

# Save the cleaned data to a new Excel file
output_file = base / "Cleaned_Data" / "iNat_vitis_vinifera_cleaned.xlsx"
df.to_excel(output_file, index=False)
print(f"Cleaned data saved to: {output_file}")