# Results

All files come from `notebooks/02_models_and_results.ipynb` (final run), except the two files marked with *, which come from `notebooks/03_paper_charts.ipynb`.

| File | Content |
|---|---|
| `stage2_results.xlsx` | Every table of the analysis. Start with the sheet "Read me", which lists all sheets |
| `feature_dictionary.xlsx` | Readable name, family and meaning of every input of the final model, and every category code with its readable label |
| `test_predictions.csv` | Predicted risk of every model version for each test crash |
| `test_crashes_with_predictions.csv` | Test crashes with their breakdown groups, location, outcome, predicted risk and whether they were flagged, for every model version |
| `shap_values_test.csv` | SHAP value and input value of the 50 most important inputs, for every test crash |
| `breakdown_tables.csv` * | Share of crashes and serious or fatal share for every breakdown group |
| `borough_map_data.csv` * | Values shown on the borough maps |

## Main sheets in `stage2_results.xlsx`

| Sheet | Content |
|---|---|
| Data and split | Crashes in the fitting, validation and test parts |
| Missing correction, Missing values | How missing values were handled |
| Selection options, Search, Search by selection | Feature selection and model search |
| Model choice, Older crashes | Choice of the final model; test of the crashes before November 2016 |
| Test results, Test comparisons | All model versions on the test part; effect of the safety score |
| Models for the paper | The final model and the other candidates |
| Photo timing check | Safety score on crashes with recent photos |
| SHAP inputs, SHAP features | Importance and direction of every input |
| Breakdowns, Top feature severity, Borough map data | Severity by group and place |
| Risk tenths, Time periods | Severity by predicted risk; results in two time periods |
| Settings, Decision log | Settings and the reason for each decision |

## Main numbers

- Full model on the test part: balanced accuracy 58.7% (57.3% to 60.3%), ROC-AUC 0.619.
- Final model: LightGBM with 82 street features plus the cyclist's age, sex and age group (85 inputs, listed in Appendix A of the paper).
