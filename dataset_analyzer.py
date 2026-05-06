"""
Author: Dilip Goswami

Purpose:
    Analyze and summarize image dataset distribution for original and
    augmented endonasal surgery image datasets.

Features:
    - Counts original images across patient/block folders
    - Counts augmented images grouped by block
    - Generates per-block and overall statistics
    - Exports summary reports to CSV and JSON
    - Validates expected folder structure before processing
    - Supports configurable output directory
    - Provides structured logging for traceability
"""

import os
import re
import json
import argparse
import logging
from pathlib import Path
from collections import defaultdict

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BLOCK_PREFIXES = ["block1", "block2", "block3"]
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset_structure(base_dir: Path) -> Path:
    """
    Validate expected dataset structure.

    Expected:
        dataset_root/
            P01/
            P02/
            ...
            Augmented Images/

    Args:
        base_dir (Path): Root dataset directory.

    Returns:
        Path: Validated augmented images directory.

    Raises:
        FileNotFoundError: If required folders are missing.
    """
    if not base_dir.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {base_dir}")

    if not base_dir.is_dir():
        raise NotADirectoryError(f"Provided path is not a directory: {base_dir}")

    augmented_dir = base_dir / "Augmented Images"

    if not augmented_dir.exists():
        raise FileNotFoundError(
            f"Missing required folder: {augmented_dir}"
        )

    patient_dirs = [
        d for d in base_dir.iterdir()
        if d.is_dir() and re.match(r"(?i)p\d{2}", d.name)
    ]

    if not patient_dirs:
        raise FileNotFoundError(
            "No patient folders found matching pattern P01, P02, etc."
        )

    logger.info("Dataset structure validation passed.")
    return augmented_dir


# ============================================================
# HELPERS
# ============================================================

def normalize_block_from_folder(folder_name: str) -> str | None:
    """Normalize BLOCK folder names into block1/block2/block3."""
    match = re.match(r"BLOCK[_\- ]?([123])", folder_name, re.IGNORECASE)
    return f"block{match.group(1)}" if match else None


def count_original_images(base_dir: Path) -> dict:
    """Count original dataset images grouped by block."""
    counts = defaultdict(int)
    visited_folders = set()

    for patient_dir in base_dir.iterdir():
        if not patient_dir.is_dir() or not re.match(r"(?i)p\d{2}", patient_dir.name):
            continue

        for side_dir in patient_dir.iterdir():
            if not side_dir.is_dir():
                continue

            for block_dir in side_dir.iterdir():
                if not block_dir.is_dir():
                    continue

                block_type = normalize_block_from_folder(block_dir.name)

                if block_type and block_dir not in visited_folders:
                    visited_folders.add(block_dir)

                    image_count = sum(
                        1 for file in block_dir.iterdir()
                        if file.suffix.lower() in IMAGE_EXTENSIONS
                    )

                    counts[block_type] += image_count

    return counts


def count_augmented_images(augmented_dir: Path) -> dict:
    """Count augmented images grouped by block."""
    counts = {block: 0 for block in BLOCK_PREFIXES}

    for block in BLOCK_PREFIXES:
        block_path = augmented_dir / block

        if not block_path.exists():
            logger.warning("Missing augmented folder: %s", block_path)
            continue

        pattern = re.compile(rf"{block}_[0-9]+\.jpe?g$", re.IGNORECASE)

        counts[block] = sum(
            1 for file in block_path.iterdir()
            if file.suffix.lower() in IMAGE_EXTENSIONS and pattern.match(file.name)
        )

    return counts


# ============================================================
# EXPORT
# ============================================================

def export_summary(
    original_counts: dict,
    augmented_counts: dict,
    total_counts: dict,
    grand_total: int,
    output_dir: Path
) -> None:
    """Export dataset summary to CSV and JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({
        "Block": BLOCK_PREFIXES,
        "Original Images": [original_counts.get(b, 0) for b in BLOCK_PREFIXES],
        "Augmented Images": [augmented_counts.get(b, 0) for b in BLOCK_PREFIXES],
        "Total Images": [total_counts[b] for b in BLOCK_PREFIXES],
    })

    df.loc[len(df)] = [
        "Total",
        sum(original_counts.values()),
        sum(augmented_counts.values()),
        grand_total
    ]

    csv_path = output_dir / "image_summary.csv"
    json_path = output_dir / "image_summary.json"

    df.to_csv(csv_path, index=False)

    with open(json_path, "w") as json_file:
        json.dump({
            "original": dict(original_counts),
            "augmented": dict(augmented_counts),
            "total": dict(total_counts),
            "grand_total": grand_total
        }, json_file, indent=4)

    logger.info("CSV exported to: %s", csv_path)
    logger.info("JSON exported to: %s", json_path)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze image distribution in dataset folders."
    )

    parser.add_argument(
        "dataset_path",
        type=Path,
        help="Path to the root dataset directory"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional custom output directory for CSV/JSON reports"
    )

    args = parser.parse_args()

    base_dir = args.dataset_path.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else base_dir

    logger.info("Starting dataset analysis...")
    logger.info("Dataset path: %s", base_dir)
    logger.info("Output path: %s", output_dir)

    augmented_dir = validate_dataset_structure(base_dir)

    original_counts = count_original_images(base_dir)
    augmented_counts = count_augmented_images(augmented_dir)

    total_counts = {
        block: original_counts.get(block, 0) + augmented_counts.get(block, 0)
        for block in BLOCK_PREFIXES
    }

    grand_total = sum(total_counts.values())

    logger.info("===== DATASET SUMMARY =====")
    for block in BLOCK_PREFIXES:
        logger.info(
            "%s | Original=%d | Augmented=%d | Total=%d",
            block,
            original_counts.get(block, 0),
            augmented_counts.get(block, 0),
            total_counts[block]
        )

    logger.info("Grand Total Images: %d", grand_total)

    export_summary(
        original_counts,
        augmented_counts,
        total_counts,
        grand_total,
        output_dir
    )

    logger.info("Dataset analysis complete.")


if __name__ == "__main__":
    main()