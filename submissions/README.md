## Submissions Folder

Place your final submission CSVs here. Use clear, date-stamped filenames, for example:

- `submission_2025-10-31_team-XYZ.csv`

### How to produce a submission
1. Prepare data in `inputs/` as needed.
2. Run the baseline (or your own pipeline) to produce a CSV under `outputs/forecasts/`.
3. Copy or move the CSV into this folder with a descriptive name.

```bash
make forecast
cp outputs/forecasts/submission.csv submissions/submission_2025-10-31_team-XYZ.csv
```

### Validate before submitting
```bash
make validate FILE=submissions/submission_2025-10-31_team-XYZ.csv
```

Validation report will be saved to `outputs/evaluation/validation.json`.

