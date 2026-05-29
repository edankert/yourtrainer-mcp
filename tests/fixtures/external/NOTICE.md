# Third-party test fixtures

These FIT files are redistributed from the **python-fitparse** project as test
fixtures and are **not** part of yourtrainer-mcp's own code.

- Source: https://github.com/dtcooper/python-fitparse (`tests/files/`)
- Licence: **MIT**
- Copyright (c) 2011–2025, David Cooper <david@dtcooper.com>
- Copyright (c) 2017–2025, Carey Metcalfe <carey@cmetcalfe.ca>

The MIT permission notice (https://github.com/dtcooper/python-fitparse/blob/master/LICENSE)
applies to the files in this directory.

## Files

| File | Purpose |
|------|---------|
| `Activity.fit` | Small real activity file — exercises the FIT reader. |
| `Edge810-Vector-2013-08-16-15-35-10.fit` | Real Garmin Edge 810 + Vector power-meter ride (4700 power samples) — reference corpus for NP/IF/TSS. |
| `garmin-edge-500-activity.fit` | Real Edge 500 ride with HR but no power — exercises FIT invalid-sentinel handling + the no-power path. |
| `WorkoutIndividualSteps.fit` | Real Garmin FIT workout (individual steps). |
| `WorkoutRepeatSteps.fit` | Real Garmin FIT workout (with a repeat block). |
| `WorkoutCustomTargetValues.fit` | Real Garmin FIT workout (custom power targets). |

Used by `tests/test_fit_real_files.py` and `tests/test_reference_corpus.py`.
