# Paste this into your script. It will plot ALL features with their NAMES
# (y-axis labels), color-code by category (object / segmentation / other),
# annotate scores on bars for the top features, and save the figure.
#
# It is robust to different CSV formats:
# - If your CSV has a "feature" column it uses that as the name.
# - If not, it will try to use the index as feature names.
# - If there is no "category" column it will infer categories from name prefixes.

import os
import re
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

IMPORTANCE_CSV = "feature_importance_summary.csv"
OUT_PLOT = "feature_importance_all_features_with_names.png"
TOP_ANNOTATE = 50   # annotate numeric score on top N bars (set 0 to disable)
MAX_LABELS_FOR_FULL_PLOT = 300  # if more features than this, show smaller font + optionally warn

if not os.path.exists(IMPORTANCE_CSV):
    raise FileNotFoundError(f"Importance CSV not found: {IMPORTANCE_CSV}")

# Load importance table (handle 'feature' col or index)
imp = pd.read_csv(IMPORTANCE_CSV)
if 'feature' in imp.columns:
    imp = imp.set_index('feature')
elif imp.columns[0] == 'Unnamed: 0' and imp['Unnamed: 0'].dtype == object:
    imp = imp.set_index('Unnamed: 0')

if 'importance_score' not in imp.columns:
    raise ValueError("importance_score column missing from importance CSV. Run the importance creation script first.")

# If category column present use it, otherwise infer from names
if 'category' in imp.columns:
    categories = imp['category'].astype(str).values
else:
    def infer_category(name):
        if re.match(r'^(obj_|object_|obj\.)', name, flags=re.I):
            return "object"
        if re.match(r'^(seg_|segmentation_|mask_|seg\.)', name, flags=re.I):
            return "segmentation"
        return "other"
    categories = [infer_category(n) for n in imp.index]

imp = imp.copy()
imp['category_inferred'] = categories

# Sort by importance
imp_sorted = imp.sort_values('importance_score', ascending=False)
feature_names = imp_sorted.index.tolist()
scores = imp_sorted['importance_score'].values
cats = imp_sorted['category_inferred'].values

# Color mapping 
color_map = {
    "object": "#1f77b4",       # blue
    "segmentation": "#2ca02c", # green
    "other": "#7f7f7f"         # gray
}
bar_colors = [color_map.get(c, "#7f7f7f") for c in cats]

# Plot sizing
n_feats = len(feature_names)
# Height per feature (in inches) — small enough to fit many features but readable
height_per_feature = 0.16
fig_height = max(6, min(140, height_per_feature * n_feats))
fig_width = 14

plt.figure(figsize=(fig_width, fig_height))
y_pos = np.arange(n_feats)

# Plot bars reversed so highest is on top
bars = plt.barh(y_pos, scores[::-1], color=np.array(bar_colors)[::-1])

# Y tick labels: feature names reversed so top is most important
plt.yticks(y_pos, np.array(feature_names)[::-1], fontsize=7 if n_feats > 80 else 9)
plt.gca().invert_yaxis()

plt.xlabel("importance_score")
plt.title("All features by importance_score (names on y-axis)")

from matplotlib.patches import Patch
handles = []
seen = set()
for cat in cats:
    if cat not in seen:
        seen.add(cat)
        handles.append(Patch(color=color_map.get(cat, "#7f7f7f"), label=cat))
plt.legend(handles=handles, title="Category", bbox_to_anchor=(1.02, 1), loc='upper left')

plt.grid(axis='x', linestyle='--', alpha=0.3)

if TOP_ANNOTATE and TOP_ANNOTATE > 0:
    n_annot = min(TOP_ANNOTATE, n_feats)
    for i in range(n_annot):
        bar_index = n_feats - 1 - i
        bar = bars[bar_index]
        score = scores[i]
        plt.text(
            bar.get_width() + 0.002,
            bar.get_y() + bar.get_height()/2,
            f"{score:.3f}",
            va='center',
            fontsize=8
        )

plt.tight_layout()
plt.savefig(OUT_PLOT, dpi=150)
plt.show()

print(f"Saved plot with feature names to: {OUT_PLOT}")
print(f"Plotted {n_feats} features. Top 20 features:")
print(imp_sorted.head(20)[['importance_score', 'category_inferred']].to_string())
