# Species Distribution Modeling (SDM) with Weighted MaxEnt

This repository contains a complete workflow for species distribution modeling using **Maximum Entropy (MaxEnt) with sample weighting**. This project is designed to predict the potential distribution of invasive species using bioclimatic, topographic, and NDVI variables while accounting for spatial and temporal bias in occurrence data.

## Project Description

This project implements an SDM pipeline that includes:
- **Data preparation** from multiple sources (GBIF, CABI, research publications)
- **Pseudo-absence generation** with various strategies (random, biased, biased-land-cover)
- **Predictive variable processing** (bioclimatic, topographic, NDVI)
- **Weighted MaxEnt model training** to address sampling bias
- **Model evaluation** with ROC-AUC and PR-AUC metrics (weighted and unweighted)
- **Distribution mapping** for historical conditions and future projections
- **Variable set comparison** for model optimization

## Project Structure

```
SDM-TOOLBOX/
│
├── 0_Iteration.ipynb                    # Main notebook to run the entire pipeline
├── 00_data-preparation.ipynb            # Occurrence data preparation and aggregation from multiple sources
├── 01_specie-distribution.ipynb         # Species distribution analysis and train/test splitting
├── 02_pseudo-absence.ipynb              # Pseudo-absence point generation
├── 03_Bioclim.ipynb                     # Bioclimatic data processing
├── 03_predictive-variables.ipynb        # Predictive variable preparation
├── 04_variable-statistics.ipynb         # Variable descriptive statistics
├── 05_run-model_weight.ipynb            # Weighted MaxEnt model training
├── 06_model-evaluation.ipynb            # Model performance evaluation
├── 07_Bioclim_mapping.ipynb             # Bioclim mapping
└── 08_variable_sets_comparison.ipynb    # Variable set comparison
```

## Workflow

### 1. Data Preparation (`00_data-preparation.ipynb`)
- Aggregates occurrence data from multiple sources:
  - GBIF (Global Biodiversity Information Facility)
  - CABI (Centre for Agriculture and Bioscience International)
  - Research publications (Otieno et al. 2019, Peng et al. 2021, etc.)
  - Field collection data
- Standardizes formats and columns
- Combines all sources into a single dataset

### 2. Species Distribution Analysis (`01_specie-distribution.ipynb`)
- Visualizes global species distribution
- Filters by geographic regions
- Splits data into training and testing sets (70:30)
- Generates multiple splits for validation (default: 10 iterations)

### 3. Pseudo-Absence Generation (`02_pseudo-absence.ipynb`)
Supported strategies:
- **Random**: Random points across the entire region
- **Biased**: Random points with bias toward easily accessible areas
- **Biased-land-cover**: Points with bias based on land cover type (prioritizing forests)

### 4. Predictive Variable Processing (`03_Bioclim.ipynb`, `03_predictive-variables.ipynb`)
- **Bioclimatic Variables**: 19 WorldClim variables (bio1-bio19)
- **Topography**: Elevation from SRTM
- **NDVI**: Normalized Difference Vegetation Index
- Support for historical data and future projections (RCP 8.5)
- Unit conversion (Kelvin to Celsius) and CRS adjustment

### 5. Model Training (`05_run-model_weight.ipynb`)
**Weighted MaxEnt Features:**
- **Distance-based weighting**: Reduces influence of overly clustered points
- **Source-based weighting**: Adjusts for data quality from different sources
- **Temporal weighting**: Gives higher weight to more recent data
- Model configuration:
  - Transform: Logistic
  - Beta multiplier: 1.5 (regularization)
  - Feature types: Linear, Hinge, Product

### 6. Model Evaluation (`06_model-evaluation.ipynb`)
Calculated metrics:
- **ROC-AUC**: Area Under ROC Curve (weighted and unweighted)
- **PR-AUC**: Precision-Recall AUC (weighted and unweighted)
- **Permutation Importance**: Importance of each predictive variable

### 7. Mapping and Visualization (`07_Bioclim_mapping.ipynb`)
- Relative Occurrence Probability (ROP) maps
- Historical vs. future prediction comparison
- Maps of potential distribution changes

### 8. Variable Set Comparison (`08_variable_sets_comparison.ipynb`)
- Evaluates performance of various bioclimatic variable combinations
- Identifies optimal variable sets

## Usage

### Initial Configuration

Edit the `0_Iteration.ipynb` notebook to set parameters:

```python
# Species selection
specie = 'leptocybe-invasa'  # or 'thaumastocoris-peregrinus'

# Geographic regions
training = 'south-east-asia'  # Region for training
interest = 'south-east-asia'  # Region for prediction/testing

# Pseudo-absence parameters
pseudoabsence = 'biased-land-cover'  # 'random', 'biased', or 'biased-land-cover'
count = 10000  # Number of background points

# Spatial resolution
ref_res = (0.01, 0.01)  # degrees (~1000m)

# Bioclimatic variables
bioclim = [i for i in range(1, 20)]  # All 19 variables

# Additional variables
topo1 = True   # Include topography
ndvi1 = True   # Include NDVI

# Number of iterations
n_iteration = 10
```

### Running the Pipeline

1. **Run the main notebook**:
   ```bash
   jupyter notebook 0_Iteration.ipynb
   ```

2. The main notebook will automatically execute other notebooks in sequence:
   - `00_data-preparation.ipynb`
   - `01_specie-distribution.ipynb`
   - `02_pseudo-absence.ipynb`
   - `03_Bioclim.ipynb`
   - `03_predictive-variables.ipynb`
   - `04_variable-statistics.ipynb`
   - `05_run-model_weight.ipynb`
   - `06_model-evaluation.ipynb`
   - `07_Bioclim_mapping.ipynb`
   - `08_variable_sets_comparison.ipynb`

## Dependencies

### Python Libraries
- `pandas` - Data manipulation
- `geopandas` - Geospatial data
- `numpy` - Numerical computing
- `xarray` & `rioxarray` - Multi-dimensional raster data
- `elapid` - Species Distribution Modeling
- `scikit-learn` - Model metrics and evaluation
- `matplotlib` & `cartopy` - Visualization and mapping
- `dask` - Parallel computing (optional)

### Data Requirements
- Species occurrence data (CSV with lat/lon columns)
- Bioclimatic rasters (WorldClim or CORDEX)
- DEM/SRTM for topography
- NDVI data (optional)
- Land cover data for land-cover-based pseudo-absence

## Output

### Output Structure
```
out/
└── {specie}/
    ├── input/
    │   ├── train/          # Training data (presence & background)
    │   ├── test/           # Testing data
    │   └── worldclim/      # Predictive variable rasters
    └── output/
        └── exp_{model}_{pseudoabsence}_{region}_{topo}_{ndvi}/
            ├── *.ela       # Trained models
            ├── *.nc        # Predictions in NetCDF format
            ├── *.tif       # Predictions in GeoTIFF format
            └── *.csv       # Input data and evaluation results
```

### Output Files
- **Distribution maps**: PNG files in `figs/` and `docs/` folders

## Supported Species (Default)
- **Leptocybe invasa** (Gall wasp on Eucalyptus)
- **Thaumastocoris peregrinus** (Bronze bug on Eucalyptus)

## Methodology

### Weighted MaxEnt
The weighted MaxEnt model addresses several limitations of standard SDM:
1. **Spatial bias**: Reduces influence of oversampled areas
2. **Temporal bias**: Gives higher weight to more recent data
3. **Data quality**: Adjusts weights based on data source
4. **Multi-source integration**: Combines data from various sources with different quality levels

### Validation
- Multiple train/test splits (default: 10 iterations)
- Evaluation on both training and testing data
- Weighted metrics for more realistic accuracy assessment

## Important Notes

1. **Data Paths**: Ensure paths to bioclimatic data and other rasters are correct in the `03_Bioclim.ipynb` notebook
2. **Memory**: This process requires sufficient memory for large raster data
3. **Dask Cluster**: For parallel computing, a Dask cluster is initialized in the main notebook
4. **Reproducibility**: Use `random_state=42` for reproducible results

## Contributing

Managing risk in SE Asian forest biosecurity – supporting evidence-based standards for best practice (ACIAR FST/2018/179)
Sub-project ‘Climate change modelling: Building biosecurity capacity for adaptation and changing risk'
