# Image Dataset Distribution Analyzer

A Python utility for analyzing and summarizing image distribution across original and augmented medical imaging datasets.

**Author:** Dilip Goswami

---

## Overview

This tool scans a structured medical imaging dataset and generates summary statistics for image distribution across dataset blocks.

It is designed for:

* Dataset auditing
* Preprocessing validation
* Augmentation verification
* Medical imaging / computer vision workflows

The script exports both human-readable and machine-readable reports for downstream analysis.

---

## Features

* Count original images across patient/block folder hierarchy
* Count augmented images grouped by block
* Combine original and augmented totals
* Export reports in CSV and JSON format
* Validate dataset folder structure before processing
* Support custom output directory
* Provide structured logging during execution

---

## Expected Dataset Structure

```text
dataset_root/
│
├── P01/
│   ├── Left/
│   │   ├── BLOCK_1/
│   │   ├── BLOCK_2/
│   │   └── BLOCK_3/
│   │
│   └── Right/
│       ├── BLOCK_1/
│       ├── BLOCK_2/
│       └── BLOCK_3/
│
├── P02/
│   └── ...
│
└── Augmented Images/
    ├── block1/
    ├── block2/
    └── block3/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/goapu/Image-Dataset-Distribution-Analyzer.git
cd Image-Dataset-Distribution-Analyzer
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Requirements

* Python 3.10+
* pandas >= 1.3.0

> **Note:** Python 3.10+ is required because the script uses modern union type hints (`str | None`).

---

## Usage

### Basic Execution

```bash
python dataset_analyzer.py /path/to/dataset
```

### Specify Custom Output Directory

```bash
python dataset_analyzer.py /path/to/dataset --output-dir ./reports
```

---

## Example Output

### CSV Report

`image_summary.csv`

| Block  | Original Images | Augmented Images | Total Images |
| ------ | --------------- | ---------------- | ------------ |
| block1 | 1200            | 600              | 1800         |
| block2 | 950             | 500              | 1450         |
| block3 | 875             | 450              | 1325         |
| Total  | 3025            | 1550             | 4575         |

---

### JSON Report

`image_summary.json`

```json
{
    "original": {
        "block1": 1200,
        "block2": 950,
        "block3": 875
    },
    "augmented": {
        "block1": 600,
        "block2": 500,
        "block3": 450
    },
    "total": {
        "block1": 1800,
        "block2": 1450,
        "block3": 1325
    },
    "grand_total": 4575
}
```

---

## Output Files

Generated in the dataset root (or specified output directory):

* `image_summary.csv`
* `image_summary.json`

---

## Use Cases

* Medical image dataset balancing verification
* Data preprocessing validation
* Augmentation pipeline auditing
* Machine learning dataset reporting
* Research supplementary analysis

---

## License

MIT License

---

## Contact

**Dilip Goswami**
For questions, feedback, or collaboration, feel free to connect via GitHub.
