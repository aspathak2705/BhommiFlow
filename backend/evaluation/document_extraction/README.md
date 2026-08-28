# Document Extraction Evaluation Framework (Dataset 2)

This directory contains the read-only evaluation code for executing document extraction benchmarks against Dataset 2 (`dataset2_document_extraction.json` and `.csv`).

## Architecture

* `loader.py`: Handles validation and safe loader parsing of ground-truth JSON/CSV files.
* `evaluator.py`: Matches the dataset fields with existing production extraction logic.
* `metrics.py`: Calculates statistics: accuracy, precision, recall, and category breakdowns.
