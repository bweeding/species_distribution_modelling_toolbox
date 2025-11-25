# Species Distribution Modeling (SDM) dengan MaxEnt Terbobot

Repositori ini berisi workflow lengkap untuk pemodelan distribusi spesies menggunakan metode **Maximum Entropy (MaxEnt) dengan pembobotan sampel**. Proyek ini dirancang untuk memprediksi distribusi potensial spesies invasif menggunakan variabel bioklimatik, topografi, dan NDVI dengan memperhitungkan bias spasial dan temporal dalam data kejadian.

## Deskripsi Proyek

Proyek ini mengimplementasikan pipeline SDM yang mencakup:
- **Persiapan data** dari berbagai sumber (GBIF, CABI, publikasi penelitian)
- **Generasi pseudo-absence** dengan berbagai strategi (random, biased, biased-land-cover)
- **Pemrosesan variabel prediktif** (bioklimatik, topografi, NDVI)
- **Pelatihan model MaxEnt terbobot** untuk mengatasi bias sampling
- **Evaluasi model** dengan metrik ROC-AUC dan PR-AUC (terbobot dan tidak terbobot)
- **Pemetaan distribusi** untuk kondisi historis dan proyeksi masa depan
- **Perbandingan set variabel** untuk optimasi model

## Struktur Proyek

```
SDM-TOOLBOX/
│
├── 0_Iteration.ipynb                    # Notebook utama untuk menjalankan seluruh pipeline
├── 00_data-preparation.ipynb            # Persiapan dan agregasi data kejadian dari berbagai sumber
├── 01_specie-distribution.ipynb         # Analisis distribusi spesies dan pembagian train/test
├── 02_pseudo-absence.ipynb              # Generasi titik pseudo-absence
├── 03_Bioclim.ipynb                     # Pemrosesan data bioklimatik
├── 03_predictive-variables.ipynb        # Persiapan variabel prediktif
├── 04_variable-statistics.ipynb         # Statistik deskriptif variabel
├── 05_run-model_weight.ipynb            # Pelatihan model MaxEnt terbobot
├── 06_model-evaluation.ipynb            # Evaluasi performa model
├── 07_Bioclim_mapping.ipynb             # Pemetaan hasil model
└── 08_variable_sets_comparison.ipynb    # Perbandingan set variabel
```

## Workflow

### 1. Persiapan Data (`00_data-preparation.ipynb`)
- Mengumpulkan data kejadian dari berbagai sumber:
  - GBIF (Global Biodiversity Information Facility)
  - CABI (Centre for Agriculture and Bioscience International)
  - Publikasi penelitian (Otieno et al. 2019, Peng et al. 2021, dll.)
  - Data koleksi lapangan
- Standardisasi format dan kolom
- Agregasi semua sumber menjadi dataset tunggal

### 2. Analisis Distribusi Spesies (`01_specie-distribution.ipynb`)
- Visualisasi distribusi global spesies
- Filtering berdasarkan wilayah geografis
- Pembagian data menjadi training dan testing (70:30)
- Generasi multiple splits untuk validasi (default: 10 iterasi)

### 3. Generasi Pseudo-Absence (`02_pseudo-absence.ipynb`)
Strategi yang didukung:
- **Random**: Titik acak di seluruh wilayah
- **Biased**: Titik acak dengan bias terhadap area yang mudah diakses
- **Biased-land-cover**: Titik dengan bias berdasarkan tipe tutupan lahan (prioritas untuk hutan)

### 4. Pemrosesan Variabel Prediktif (`03_Bioclim.ipynb`, `03_predictive-variables.ipynb`)
- **Variabel Bioklimatik**: 19 variabel WorldClim (bio1-bio19)
- **Topografi**: Elevasi dari SRTM
- **NDVI**: Normalized Difference Vegetation Index
- Dukungan untuk data historis dan proyeksi masa depan (RCP 8.5)
- Konversi unit (Kelvin ke Celsius) dan penyesuaian CRS

### 5. Pelatihan Model (`05_run-model_weight.ipynb`)
**Fitur MaxEnt Terbobot:**
- **Pembobotan berbasis jarak**: Mengurangi pengaruh titik yang terlalu rapat
- **Pembobotan berbasis sumber data**: Menyesuaikan kualitas data dari berbagai sumber
- **Pembobotan temporal**: Memberikan bobot lebih tinggi pada data terbaru
- Konfigurasi model:
  - Transformasi: Logistic
  - Beta multiplier: 1.5 (regularisasi)
  - Feature types: Linear, Hinge, Product

### 6. Evaluasi Model (`06_model-evaluation.ipynb`)
Metrik yang dihitung:
- **ROC-AUC**: Area Under ROC Curve (terbobot dan tidak terbobot)
- **PR-AUC**: Precision-Recall AUC (terbobot dan tidak terbobot)
- **Permutation Importance**: Pentingnya setiap variabel prediktif

### 7. Pemetaan dan Visualisasi (`07_Bioclim_mapping.ipynb`)
- Peta probabilitas kejadian relatif (Relative Occurrence Probability)
- Perbandingan prediksi historis vs. masa depan
- Peta perubahan distribusi potensial

### 8. Perbandingan Set Variabel (`08_variable_sets_comparison.ipynb`)
- Evaluasi performa berbagai kombinasi variabel bioklimatik
- Identifikasi set variabel optimal

## Penggunaan

### Konfigurasi Awal

Edit notebook `0_Iteration.ipynb` untuk mengatur parameter:

```python
# Pilihan spesies
specie = 'leptocybe-invasa'  # atau 'thaumastocoris-peregrinus'

# Wilayah geografis
training = 'south-east-asia'  # Wilayah untuk pelatihan
interest = 'south-east-asia'  # Wilayah untuk prediksi/testing

# Parameter pseudo-absence
pseudoabsence = 'biased-land-cover'  # 'random', 'biased', atau 'biased-land-cover'
count = 10000  # Jumlah titik background

# Resolusi spasial
ref_res = (0.01, 0.01)  # derajat (~1000m)

# Variabel bioklimatik
bioclim = [i for i in range(1, 20)]  # Semua 19 variabel

# Variabel tambahan
topo1 = True   # Sertakan topografi
ndvi1 = True   # Sertakan NDVI

# Jumlah iterasi
n_iteration = 10
```

### Menjalankan Pipeline

1. **Jalankan notebook utama**:
   ```bash
   jupyter notebook 0_Iteration.ipynb
   ```

2. Notebook utama akan secara otomatis menjalankan notebook-notebook lainnya secara berurutan:
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
- `pandas` - Manipulasi data
- `geopandas` - Data geospasial
- `numpy` - Komputasi numerik
- `xarray` & `rioxarray` - Data raster multi-dimensi
- `elapid` - Species Distribution Modeling
- `scikit-learn` - Metrik dan evaluasi model
- `matplotlib` & `cartopy` - Visualisasi dan pemetaan
- `dask` - Komputasi paralel (opsional)

### Data Requirements
- Data kejadian spesies (CSV dengan kolom lat/lon)
- Raster bioklimatik (WorldClim atau CORDEX)
- DEM/SRTM untuk topografi
- Data NDVI (opsional)
- Data tutupan lahan untuk pseudo-absence berbasis land-cover

## Output

### Struktur Output
```
out/
└── {specie}/
    ├── input/
    │   ├── train/          # Data training (presence & background)
    │   ├── test/           # Data testing
    │   └── worldclim/      # Raster variabel prediktif
    └── output/
        └── exp_{model}_{pseudoabsence}_{region}_{topo}_{ndvi}/
            ├── *.ela       # Model terlatih
            ├── *.nc        # Prediksi dalam format NetCDF
            ├── *.tif       # Prediksi dalam format GeoTIFF
            └── *.csv       # Data input dan hasil evaluasi
```

### File Hasil
- **Peta distribusi**: PNG files di folder `figs/` dan `docs/`

## Spesies yang Didukung (Default)

- **Leptocybe invasa** (Gall wasp pada Eucalyptus)
- **Thaumastocoris peregrinus** (Bronze bug pada Eucalyptus)

## Metodologi

### MaxEnt dengan Pembobotan
Model MaxEnt terbobot mengatasi beberapa keterbatasan SDM standar:
1. **Bias spasial**: Mengurangi pengaruh area yang terlalu banyak sampling
2. **Bias temporal**: Memberikan bobot lebih pada data terbaru
3. **Kualitas data**: Menyesuaikan bobot berdasarkan sumber data
4. **Integrasi multi-sumber**: Menggabungkan data dari berbagai sumber dengan kualitas berbeda

### Validasi
- Multiple train/test splits (default: 10 iterasi)
- Evaluasi pada data training dan testing
- Metrik terbobot untuk akurasi yang lebih realistis

## Catatan Penting

1. **Path Data**: Pastikan path ke data bioklimatik dan raster lainnya sudah benar di notebook `03_Bioclim.ipynb`
2. **Memory**: Proses ini membutuhkan memori yang cukup untuk data raster besar
3. **Dask Cluster**: Untuk komputasi paralel, cluster Dask diinisialisasi di notebook utama
4. **Reproducibility**: Gunakan `random_state=42` untuk hasil yang dapat direproduksi

## Kontribusi

Managing risk in SE Asian forest biosecurity – supporting evidence-based standards for best practice (ACIAR FST/2018/179)
Sub-project ‘Climate change modelling: Building biosecurity capacity for adaptation and changing risk'

