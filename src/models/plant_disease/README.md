# Data Files

This directory contains the disease information and treatment recommendation databases.

## Files

### disease_info.csv
Contains information about each of the 39 plant diseases:
- `disease_name`: Human-readable disease name
- `description`: Detailed description of the disease
- `Possible Steps`: Prevention and treatment steps
- `image_url`: Reference image URL

### supplement_info.csv
Contains treatment and supplement recommendations:
- `supplement name`: Recommended treatment/product name
- `supplement image`: Product image URL
- `buy link`: Purchase link for the product

## Usage

These CSV files are loaded by the `disease_service.py` when initializing the detector:

```python
from services.disease_service import init_detector

init_detector(
    model_path='models/plant_disease_model_1_latest.pt',
    disease_info_path='data/disease_info.csv',
    supplement_info_path='data/supplement_info.csv'
)
```

## Format

Both files use CSV format with `cp1252` encoding to support special characters.
