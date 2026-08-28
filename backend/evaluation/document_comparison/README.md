# Document Comparison Evaluation Framework (Dataset 3)

This directory contains the read-only evaluation code for executing comparison scenario benchmarks against Dataset 3 (`dataset3_document_comparison.json`).

## Architecture

* `loader.py`: Handles validation and safe loader parsing of ground-truth JSON files.
* `evaluator.py`: Matches the dataset fields with mock-simulated metadata or text representations to evaluate rules.
* `metrics.py`: Calculates statistics: accuracy, precision, recall, and category breakdowns.
