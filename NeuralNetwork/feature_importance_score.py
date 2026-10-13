# !pip install azure-storage-blob pandas numpy scikit-learn tensorflow

import os
import json
import pandas as pd
import numpy as np
from io import StringIO
from azure.storage.blob import BlobServiceClient
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from tqdm.notebook import tqdm
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from typing import Dict, Any, List
AZURE_CONNECTION_STRING = "conn"

"""
Create a feature importance summary CSV using a rank-ensemble 'importance_score'.

Produces: feature_importance_summary.csv

Metrics combined:
 - variance (on standardized features)
 - ANOVA F-value (f_classif)
 - Mutual Information (mutual_info_classif)
 - RandomForest feature_importance (balanced RF on 70% train split)
 - max absolute per-class effect size (Cohen's d)

Behavior:
 - Auto-detects a target column by name heuristics (safety, bin, label, target, class).
 - If numeric with >20 unique values, it will bin into 5 quantiles.
 - Converts non-numeric feature columns to numeric (coerce), fills NaN with 0.0.
 - Adds simple category tags (obj / seg / other) based on feature name prefixes.
"""

import os
import re
import numpy as np
import pandas as pd
import warnings

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ----------------- CONFIG -----------------
FEATURES_CSV = "processed_features_conf_0.7.csv"   # input (features + possible target)
OUT_CSV = "feature_importance_summary.csv"         # output summary
RANDOM_STATE = 42
RF_ESTIMATORS = 200
RF_TEST_SIZE = 0.30   # train RF on 70% to reduce overfit
# ------------------------------------------

# helper: detect a target column
def detect_target_col(df):
    candidate_target_cols = [c for c in df.columns if any(k in c.lower() for k in ("safety", "label", "target", "bin", "class", "y"))]
    if not candidate_target_cols:
        return None
    # prefer specific names
    for prefer in ("safety_bin", "safety", "safety_score", "label", "target", "class", "bin"):
        for c in candidate_target_cols:
            if prefer in c.lower():
                return c
    return candidate_target_cols[0]

# Load
if not os.path.exists(FEATURES_CSV):
    raise FileNotFoundError(f"Features CSV not found: {FEATURES_CSV}")

df_full = pd.read_csv(FEATURES_CSV, index_col=0)
print("Loaded:", FEATURES_CSV, "shape:", df_full.shape)

# Detect target
target_col = detect_target_col(df_full)
if target_col is None:
    raise ValueError("No target column found by heuristics. Rename your target to include 'safety', 'bin', 'label', 'target' or 'class'.")

print("Using target column:", target_col)

# Split features and target
y_series = df_full[target_col].copy()
X_df = df_full.drop(columns=[target_col]).copy()

# Ensure features numeric: coerce non-numeric -> NaN -> fill 0
for c in X_df.columns:
    X_df[c] = pd.to_numeric(X_df[c], errors='coerce')
X_df = X_df.fillna(0.0)

# Prepare y (encode if necessary; bin if too many unique numeric values)
if pd.api.types.is_integer_dtype(y_series) or pd.api.types.is_float_dtype(y_series):
    nunique = int(y_series.nunique())
    print("Target numeric, unique values:", nunique)
    if nunique > 20:
        # bin into 5 quantiles
        y_binned, bins = pd.qcut(y_series, q=5, labels=False, retbins=True, duplicates='drop')
        y = y_binned.values
        class_names = [f"Bin_{i}" for i in range(len(np.unique(y)))]
        print("Binned numeric target into", len(class_names), "quantile classes.")
    else:
        le = LabelEncoder()
        y = le.fit_transform(y_series.values)
        class_names = [str(cl) for cl in le.classes_]
else:
    le = LabelEncoder()
    y = le.fit_transform(y_series.astype(str).values)
    class_names = [str(cl) for cl in le.classes_]

n_classes = len(np.unique(y))
print("Number of classes used:", n_classes)

# Standardize features for metrics that require it
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_df.values)  # ndarray shape (n_samples, n_features)
feat_names = X_df.columns.tolist()
n_feats = len(feat_names)
print("Number of features:", n_feats)

# Prepare results DataFrame
results = pd.DataFrame(index=feat_names)
results["variance"] = np.var(X_scaled, axis=0)
results["mean_abs"] = np.mean(np.abs(X_scaled), axis=0)

# Suppress known sklearn warnings for constant features during ANOVA
warnings.filterwarnings("ignore", message="Features .* are constant.")

# 1) ANOVA F-value
try:
    f_vals, p_vals = f_classif(X_scaled, y)
except Exception as e:
    # if something fails, populate NaNs
    f_vals = np.full(n_feats, np.nan)
    p_vals = np.full(n_feats, np.nan)
    print("f_classif failed:", e)
results["f_value"] = f_vals
results["f_pvalue"] = p_vals

# 2) Mutual Information
try:
    mi = mutual_info_classif(X_scaled, y, discrete_features=False, random_state=RANDOM_STATE)
except Exception as e:
    mi = np.full(n_feats, np.nan)
    print("mutual_info_classif failed:", e)
results["mutual_info"] = mi

# 3) Random Forest importance (train/test split to reduce overfit)
X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=RF_TEST_SIZE,
                                          random_state=RANDOM_STATE, stratify=y)
rf = RandomForestClassifier(n_estimators=RF_ESTIMATORS, random_state=RANDOM_STATE,
                            class_weight='balanced', n_jobs=-1)
rf.fit(X_tr, y_tr)
rf_imp = rf.feature_importances_
results["rf_importance"] = rf_imp

# 4) Per-class effect sizes (Cohen's d) and aggregates
for cls in np.unique(y):
    cls_mask = (y == cls)
    others_mask = ~cls_mask
    # mean difference
    mean_cls = X_scaled[cls_mask].mean(axis=0)
    mean_oth = X_scaled[others_mask].mean(axis=0)
    # pooled std
    var_cls = X_scaled[cls_mask].var(axis=0, ddof=0)
    var_oth = X_scaled[others_mask].var(axis=0, ddof=0)
    pooled_std = np.sqrt((var_cls + var_oth) / 2.0)
    pooled_std[pooled_std == 0] = 1e-9
    cohens_d = (mean_cls - mean_oth) / pooled_std
    results[f"effect_size_class_{cls}"] = cohens_d

# Aggregate effect sizes
effect_cols = [c for c in results.columns if c.startswith("effect_size_class_")]
if effect_cols:
    abs_stack = np.abs(results[effect_cols].values)
    results["max_abs_effect_size"] = np.max(abs_stack, axis=1)
    results["mean_abs_effect_size"] = np.mean(abs_stack, axis=1)
else:
    results["max_abs_effect_size"] = 0.0
    results["mean_abs_effect_size"] = 0.0

# 5) Rank-ensemble -> importance_score
rank_cols = ["variance", "f_value", "mutual_info", "rf_importance", "max_abs_effect_size"]
# If some rank cols are missing (NaN), ranking will still work; fill NaN with lowest possible value before ranking
rtemp = results[rank_cols].copy()
# Replace -inf/inf with NaN, then fill NaN with very small numbers so they rank low
rtemp = rtemp.replace([np.inf, -np.inf], np.nan).fillna(0.0)

ranks = rtemp.rank(ascending=False, method='average', na_option='bottom')
results["mean_rank"] = ranks.mean(axis=1)

# Normalize mean_rank to 0..1, invert so higher importance -> closer to 1
min_r = results["mean_rank"].min()
max_r = results["mean_rank"].max()
if max_r == min_r:
    results["importance_score"] = 1.0
else:
    results["importance_score"] = 1.0 - ((results["mean_rank"] - min_r) / (max_r - min_r))

# Add simple category tags based on prefix
def categorize_feature(name):
    if re.match(r'^(obj_|object_|obj\.)', name, flags=re.I):
        return "object"
    if re.match(r'^(seg_|segmentation_|mask_|seg\.)', name, flags=re.I):
        return "segmentation"
    return "other"

results["category"] = [categorize_feature(n) for n in results.index]

# Reorder columns for readability
ordered_cols = ["category", "variance", "f_value", "f_pvalue", "mutual_info",
                "rf_importance", "max_abs_effect_size", "mean_abs_effect_size",
                "mean_rank", "importance_score"] + effect_cols
ordered_cols = [c for c in ordered_cols if c in results.columns]  # guard

results = results[ordered_cols]

# Save CSV
results.to_csv(OUT_CSV, index=True)
print("Saved importance summary to:", OUT_CSV)

# Print top 20 features
print("\nTop 20 by importance_score:")
print(results.sort_values("importance_score", ascending=False).head(20)[["importance_score", "category"]])
