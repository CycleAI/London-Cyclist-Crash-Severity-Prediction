import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import time

from sklearn.feature_selection import mutual_info_classif
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, ParameterGrid
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report, balanced_accuracy_score
# Requires: pip install imbalanced-learn
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import ADASYN

warnings.filterwarnings("ignore")

# -------------------------
# CONFIG
# -------------------------
CSV_PATH = 'enriched_collision_data_100m_new.csv'
POS_CLASS = 'Serious/Fatal'
N_SPLITS = 5
N_REPEATS = 3
RANDOM_STATE = 42
TOP_K_MI = 20  

# 1. Load and Prepare
df = pd.read_csv(CSV_PATH)

df['Severity_Binary'] = df['Severity'].replace({'Fatal': 'Serious/Fatal', 'Serious': 'Serious/Fatal'})

le = LabelEncoder()
y = le.fit_transform(df['Severity_Binary'])
class_names = list(le.classes_)
pos_label_idx = int(np.where(np.array(class_names) == POS_CLASS)[0][0])
other_label_idx = 1 - pos_label_idx

# ----------------------------------------------------------------
# NEW: GLOBAL FEATURE SELECTION (EXTRACT ONCE)
# ----------------------------------------------------------------
X_init = df.drop(columns=['Severity', 'Severity_Binary'], errors='ignore').select_dtypes(include=[np.number])

# Temporary preparation for MI calculation
X_mi_temp = X_init.fillna(X_init.median()).fillna(0)
dense_cols = X_mi_temp.columns[(X_mi_temp > 0).mean() > 0.10]
if len(dense_cols) == 0:
    dense_cols = X_mi_temp.columns
X_mi_temp = X_mi_temp[dense_cols]

print(f"Calculating Mutual Information once for all features...")
mi_scores = mutual_info_classif(X_mi_temp, y, random_state=RANDOM_STATE)
mi_series = pd.Series(mi_scores, index=X_mi_temp.columns).sort_values(ascending=False)
top_k = min(TOP_K_MI, len(mi_series))
SELECTED_FEATURES = mi_series.head(top_k).index.tolist()

print(f"Features selected: {SELECTED_FEATURES}")

# Filter X_all to only use these features globally
X_all = X_init[SELECTED_FEATURES]

# ----------------------------------------------------------------
# STEP 1: MANUAL GRID SEARCH WITH THRESHOLDS & STD DEV
# ----------------------------------------------------------------
param_grid = {
    "clf__estimator__hidden_layer_sizes": [(8,8), (8,4), (16,8), (8,)],
    "clf__estimator__alpha": [1e-4, 1e-3],
    "sampler__sampling_strategy": [0.7, 1.0],
    "sampler__n_neighbors": [3, 5],
    "clf__threshold": [0.40, 0.45],
}

candidates = list(ParameterGrid(param_grid))
total_candidates = len(candidates)

print(f"Total Candidates: {total_candidates}")
print(f"Executing {N_REPEATS * N_SPLITS} fits per candidate (Total: {total_candidates * (N_REPEATS * N_SPLITS)})")
print("-" * 115)
print(f"{'#':<4} | {'Layers':<12} | {'Alpha':<8} | {'Samp':<5} | {'Neigh':<5} | {'Thresh':<6} | {'Bal. Acc':<10} | {'Std Dev':<9} | {'Status'}")
print("-" * 115)

results_list = []
best_score = -1
best_params_overall = None

# Manual Loop for Live Updates
for i, params in enumerate(candidates):

    mlp_args = {
        'hidden_layer_sizes': params['clf__estimator__hidden_layer_sizes'],
        'alpha': params['clf__estimator__alpha'],
        'max_iter': 500,
        'early_stopping': True,
        'random_state': RANDOM_STATE
    }

    ada_args = {
        'sampling_strategy': params['sampler__sampling_strategy'],
        'n_neighbors': params['sampler__n_neighbors'],
        'random_state': RANDOM_STATE
    }

    current_threshold = params['clf__threshold']

    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE)
    fold_scores = []

    try:
        for train_idx, val_idx in cv.split(X_all, y):
            X_tr_raw = X_all.iloc[train_idx].copy()
            X_val_raw = X_all.iloc[val_idx].copy()
            y_tr, y_val = y[train_idx], y[val_idx]

            # Impute using training medians
            medians = X_tr_raw.median()
            X_tr = X_tr_raw.fillna(medians).fillna(0)
            X_val = X_val_raw.fillna(medians).fillna(0)

            # Scaling
            scaler = StandardScaler()
            X_tr_scaled = scaler.fit_transform(X_tr)
            X_val_scaled = scaler.transform(X_val)

            # ADASYN + MLP
            ada = ADASYN(**ada_args)
            X_res, y_res = ada.fit_resample(X_tr_scaled, y_tr)

            mlp = MLPClassifier(**mlp_args)
            mlp.fit(X_res, y_res)

            probs = mlp.predict_proba(X_val_scaled)[:, pos_label_idx]
            preds = np.where(probs > current_threshold, pos_label_idx, other_label_idx)

            fold_scores.append(balanced_accuracy_score(y_val, preds))

        mean_score = np.mean(fold_scores)
        std_score = np.std(fold_scores, ddof=1) if len(fold_scores) > 1 else 0.0

    except Exception:
        mean_score = 0.0
        std_score = 0.0

    if mean_score > best_score:
        best_score = mean_score
        best_params_overall = {
            'mlp_args': mlp_args,
            'ada_args': ada_args,
            'threshold': current_threshold,
            'std': std_score
        }

    # LIVE PRINTING (Restored)
    layers_str = str(mlp_args['hidden_layer_sizes'])
    print(f"{i+1:<4} | {layers_str:<12} | {mlp_args['alpha']:<8} | {ada_args['sampling_strategy']:<5} | "
          f"{ada_args['n_neighbors']:<5} | {current_threshold:<6} | {mean_score:.4f}     | {std_score:.4f}    | "
          f"{total_candidates - (i+1)} left")

# ----------------------------------------------------------------
# STEP 2: FINAL EVALUATION (Using global features)
# ----------------------------------------------------------------
print("\n" + "="*50)
print(f"WINNER FOUND")
print(f"Balanced Acc: {best_score:.4f} (+/- {best_params_overall['std']:.4f})")
print(f"Threshold: {best_params_overall['threshold']}")
print(f"Layers: {best_params_overall['mlp_args']['hidden_layer_sizes']}")
print("="*50)

all_y_true, all_y_pred = [], []
aggregate_cm = np.zeros((2, 2), dtype=int)

cv_eval = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE)

for train_idx, test_idx in cv_eval.split(X_all, y):
    X_tr_raw = X_all.iloc[train_idx].copy()
    X_te_raw = X_all.iloc[test_idx].copy()
    y_tr, y_te = y[train_idx], y[test_idx]

    medians = X_tr_raw.median()
    X_tr = X_tr_raw.fillna(medians).fillna(0)
    X_te = X_te_raw.fillna(medians).fillna(0)

    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr)
    X_te_scaled = scaler.transform(X_te)

    ada_final = ADASYN(**best_params_overall['ada_args'])
    X_res, y_res = ada_final.fit_resample(X_tr_scaled, y_tr)

    mlp_final = MLPClassifier(**best_params_overall['mlp_args'])
    mlp_final.fit(X_res, y_res)

    probs = mlp_final.predict_proba(X_te_scaled)[:, pos_label_idx]
    preds = np.where(probs > best_params_overall['threshold'], pos_label_idx, other_label_idx)

    all_y_true.extend(y_te)
    all_y_pred.extend(preds)
    aggregate_cm += confusion_matrix(y_te, preds, labels=[0, 1])

print("\n=== FINAL CLASSIFICATION REPORT ===")
print(classification_report(all_y_true, all_y_pred, target_names=class_names, digits=4))

# Visualization
plt.figure(figsize=(7, 6))
sns.heatmap(aggregate_cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title(f"Final Model Results\nMean Balanced Acc: {best_score:.4f} (Threshold: {best_params_overall['threshold']})")
plt.ylabel('True Class')
plt.xlabel('Predicted Class')
plt.tight_layout()
plt.show()
