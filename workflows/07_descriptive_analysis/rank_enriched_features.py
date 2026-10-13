import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import mutual_info_classif

df = pd.read_csv('enriched_collision_data_500m_new.csv')

# 1. Drop entirely empty columns and constants
df = df.dropna(axis=1, how='all')
constant_cols = [c for c in df.columns if df[c].nunique() <= 1]
X = df.drop(columns=['Severity','accident_severity_normalized'] + constant_cols, errors='ignore')
y = df['Severity']

# 2. Handle Sparse Features (seg_ and obj_)
# These should be 0 if missing, as it implies non-existence
seg_obj_cols = [c for c in X.columns if c.startswith(('seg_', 'obj_'))]
X[seg_obj_cols] = X[seg_obj_cols].fillna(0)

# 3. Handle Remaining Types
# Numeric: Median
for c in X.select_dtypes(include=[np.number]).columns:
    if c not in seg_obj_cols:
        X[c] = X[c].fillna(X[c].median())

# Categorical: Placeholder + LabelEncode
for c in X.select_dtypes(include=['object','category']).columns:
    X[c] = X[c].fillna('___MISSING___')
    X[c] = LabelEncoder().fit_transform(X[c].astype(str))

# Bools to Int
for c in X.select_dtypes(include=['bool']).columns:
    X[c] = X[c].astype(int)

# 4. Target Encode
y_enc = LabelEncoder().fit_transform(y)

# 5. Discrete Mask
# Ensure continuous seg_ columns (floats) are NOT marked as discrete
orig_cat_cols = list(df.select_dtypes(include=['object','category']).columns)
discrete_cols = orig_cat_cols + [c for c in X.columns if pd.api.types.is_integer_dtype(X[c].dtype)]
# Important: exclude the seg_ columns from discrete even if they were integers (though they are floats)
discrete_mask = [c in discrete_cols for c in X.columns]

mi = mutual_info_classif(X, y_enc, discrete_features=discrete_mask, random_state=42, n_neighbors=5)
mi_series = pd.Series(mi, index=X.columns).sort_values(ascending=False)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(mi_series.head)
