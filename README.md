# Host Occurrence Data Pipeline for Invasive Species Research
### Cleaning, standardizing, and preparing host records from GBIF and iNaturalist for ecological modeling and geospatial analysis

This project supports invasive species research by cleaning and organizing host occurrence data from sources such as GBIF and iNaturalist. The pipeline standardizes raw biodiversity records, removes low-quality or inconsistent observations, and prepares cleaned datasets for later geospatial analysis, ecological modeling, and species distribution studies.

## Research Objective
The goal of this project is to prepare reliable host occurrence datasets for use in invasive species research, including species distribution modeling, spread forecasting, and geospatial analysis.

## Installation and Setup
1. **Prerequisites**: Ensure you have Python 3.8 or higher installed on your system.

2. **Clone or Download the Repository**: If hosted on GitHub, clone the repository using:
   ```
   git clone <repository-url>
   ```
   Or, download and extract the project files to your local machine.

3. **Set Up Virtual Environment**:
   - Navigate to the project directory.
   - Create a virtual environment (if not already present):
     `
     python -m venv .venv
     `
   - Activate the virtual environment:
     - On Windows: `.venv\Scripts\activate`
     - On macOS/Linux: `source .venv/bin/activate`

4. **Install Dependencies**:
   - Install required Python packages:
     ```
     pip install pandas numpy scipy rasterio openpyxl
     ```
   - If you have a `requirements.txt` file (check the project root), use:
     ```
     pip install -r requirements.txt
     ```

5. **Verify Setup**: Run a simple test script to ensure everything is working, e.g., `python -c "import pandas; print('Setup complete')"`.

## Data Sources and Structure
### Data Sources
- **GBIF (Global Biodiversity Information Facility)**: Provides raw biodiversity occurrence data for various species, including coordinates, dates, and metadata.
- **iNaturalist**: Community-contributed observations with location data, photos, and species identifications.

Raw data from these sources is stored in the `Raw_Data/` folder

### Folder Structure
Host_Occurrence_Data_Pipeline/
│
├── Raw_Data/
│   ├── GBIF/
│   │   └── Raw Excel/CSV files downloaded from GBIF, containing full metadata for each species.
│   └── iNaturalist/
│       └── Raw CSV files from iNaturalist exports, with observation details and coordinates.
│
├── Cleaned_Data/
│   ├── Initial_Cleaning/
│   │   └── Datasets after quality control: removes records with missing latitude/longitude, filters out coordinate uncertainty >1000m, standardizes columns (species, decimalLatitude, decimalLongitude, dateIdentified, coordinateUncertaintyInMeters).
│   │
│   ├── Cleaning2and3/
│   │   └── Combined datasets from GBIF and iNaturalist: merges sources, standardizes column names (e.g., renaming iNat 'latitude' to 'decimalLatitude'), removes duplicates, ensures consistent data types.
│   │
│   └── Fully_Thinned_Data/
│       └── Spatially thinned datasets: reduces to one observation per ~1km raster cell to minimize spatial clustering and redundancy for modeling.
│
├── Climate_Data/
│   └── Climate raster files (e.g., WorldClim bioclimatic variables like BIO1 temperature) used for filtering records based on environmental suitability.
│
├── Scripts/
│   ├── Initial cleaning scripts: Filter missing coords and high uncertainty.
│   ├── Merging/standardization scripts: Combine GBIF/iNat data and standardize columns.
│   ├── Spatial thinning scripts: Apply raster-based thinning.
│   └── Climate-based filtering scripts: Extract and filter by climate values.
│
└── README.md

## Usage/Running the Pipeline
Follow these steps to run the data cleaning pipeline. Ensure your virtual environment is activated and dependencies are installed.

1. **Initial Cleaning**:
   - Run scripts to clean raw data from GBIF and iNaturalist.
   - Example: `python Scripts/gbif_coords_and_uncertainty.py` (adjust file paths in script as needed).
   - Expected output: Cleaned CSV files in `Cleaned_Data/InitialCleaning/` with filtered coordinates and uncertainty.

2. **Combining and Standardizing (Phase 2 and 3)**:
   - Merge cleaned GBIF and iNaturalist data for each species.
   - Example: `python Scripts/Phase2and3_loopApproach.py` or `python Scripts/Phase2and3_TreeApproach.py`.
   - Expected output: Combined CSV files in `Cleaned_Data/Cleaning2and3/` with standardized columns.

3. **Spatial Thinning**:
   - Apply thinning to reduce spatial clustering.
   - Example: Run the thinning logic within Phase2and3 scripts or separately if modified.
   - Expected output: Thinned CSV files in `Cleaned_Data/Fully_thinned_data/` with reduced record density.

4. **Climate Filtering**:
   - Filter records based on climate data.
   - Example: `python Scripts/Climate_Filtering.py`.
   - Expected output: Climate-filtered CSV files, e.g., in `Cleaned_Data/` with added climate variables.

Modify script file paths as needed for your specific datasets. Scripts print progress and record counts to the console. For batch processing multiple species, loop over files or adapt scripts accordingly.

## Scripts Overview
- **gbif_coords_and_uncertainty.py**: Cleans GBIF data. Input: Raw GBIF Excel/CSV. Output: Filtered CSV with valid coordinates and uncertainty <1000m.
- **iNat_coords_and_uncertainty.py**: Cleans iNaturalist data. Input: Raw iNat CSV. Output: Filtered CSV with valid coordinates and positional accuracy.
- **Phase2and3_loopApproach.py**: Combines and thins GBIF/iNat data using loops. Input: Cleaned GBIF/iNat CSVs. Output: Combined and thinned CSV per species.
- **Phase2and3_TreeApproach.py**: Combines and thins data using KDTree for efficiency. Input: Cleaned CSVs. Output: Combined and spatially thinned CSV.
- **Climate_Filtering.py**: Filters data based on climate rasters. Input: Thinned CSV and climate TIFF. Output: Climate-filtered CSV with extracted values.
