# Models

`final_models.joblib` contains the street and full models of the final run (LightGBM, trained on the fitting and validation parts, 85% of the crashes).

## Load and predict

```python
import joblib
import numpy as np
import pandas as pd

saved = joblib.load("final_models.joblib")
print(saved["final model"], saved["how to predict"])

version = "Full"                                   # or "Street"
table = pd.read_csv("../data/eligible_pre_crash_inputs.csv")
scores = []
for member, parts in saved[version].items():
    X = parts["preprocessor"].transform(table[parts["cols"]])
    scores.append(np.mean([m.predict_proba(X)[:, 1] for m in parts["models"]], axis=0))
risk = np.mean(scores, axis=0)
```

The scores rank crashes by risk; they are not calibrated probabilities. To flag crashes, the final run flagged the same share of crashes as chosen on the validation part (stored in `saved["cut-offs (share of crashes flagged)"]`).

## Requirements

The model file needs the same package versions as the final run (see `requirements.txt`), in particular scikit-learn 1.6.1 and LightGBM 4.6.0.
