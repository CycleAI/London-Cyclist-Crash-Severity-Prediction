import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# ---- Helpers ----
def latlon_to_ecef(lat_deg, lon_deg, h=0.0):
    """
    Convert latitude/longitude (degrees) to ECEF Cartesian coordinates (meters)
    using the WGS84 ellipsoid.
    Returns array shape (N,3).
    """
    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    a = 6378137.0  # semi-major axis (m)
    f = 1.0 / 298.257223563  # flattening
    e2 = f * (2 - f)

    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    sin_lon = np.sin(lon)
    cos_lon = np.cos(lon)

    N = a / np.sqrt(1.0 - e2 * sin_lat * sin_lat)
    x = (N + h) * cos_lat * cos_lon
    y = (N + h) * cos_lat * sin_lon
    z = ((1.0 - e2) * N + h) * sin_lat

    return np.column_stack((x, y, z))


# ---- 1. Load the datasets ----
collision_df = pd.read_csv('final_mapped_accidents.csv')
mapping_df = pd.read_csv('metadata_images_mapping.csv')
features_df = pd.read_csv('processed_features_conf_0.5_probs.csv')

# Clean missing values
mapping_df = mapping_df.dropna(subset=['image_blob_name', 'lat', 'lng'])
features_df = features_df.dropna(subset=['image_name'])

# ---- 2. Link Features to Coordinates ----
# Extract the base filename (e.g., '4411_0.jpg') from the full blob path
mapping_df['image_filename'] = mapping_df['image_blob_name'].astype(str).apply(lambda x: x.split('/')[-1])

# Merge visual features with their lat/lng coordinates
visual_data = pd.merge(
    features_df,
    mapping_df[['image_filename', 'lat', 'lng']],
    left_on='image_name',
    right_on='image_filename',
    how='inner'
)

# === ADD THIS RIGHT AFTER the visual_data = pd.merge(...) line ===
# compute per-location object counts (how many images at the same lat/lng detected each obj)
OBJ_THRESH = 0.0  # object considered "present" if probability > OBJ_THRESH
obj_cols = [c for c in visual_data.columns if c.startswith('obj_')]
if obj_cols:
    # make a copy of only lat/lng + obj cols, treat NaN as 0
    _pres = visual_data[['lat', 'lng'] + obj_cols].copy()
    _pres[obj_cols] = (_pres[obj_cols].fillna(0) > OBJ_THRESH).astype(int)
    obj_counts_df = _pres.groupby(['lat', 'lng'])[obj_cols].sum().reset_index()
    # rename to obj_<name>_count
    obj_counts_df = obj_counts_df.rename(columns={c: f"{c}_count" for c in obj_cols})
else:
    obj_counts_df = None
# === END ADDITION ===

# Average the features for the 4 image angles at each unique location
visual_features_per_loc = visual_data.drop(columns=['image_name', 'image_filename']).groupby(['lat', 'lng']).mean().reset_index()
# === ADD THIS RIGHT AFTER the visual_features_per_loc = ...groupby(...).mean().reset_index() line ===
# merge the computed object counts into the per-location averaged features
if obj_counts_df is not None:
    visual_features_per_loc = visual_features_per_loc.merge(obj_counts_df, on=['lat', 'lng'], how='left')
    # fill any missing counts (locations without counts) with 0 and cast to int
    for c in obj_cols:
        cnt_col = f"{c}_count"
        if cnt_col in visual_features_per_loc.columns:
            visual_features_per_loc[cnt_col] = visual_features_per_loc[cnt_col].fillna(0).astype(int)
# === END ADDITION ===
# if no visual points, exit gracefully
if visual_features_per_loc.shape[0] == 0:
    raise SystemExit("No visual feature locations found after merging — check your inputs.")

# ---- 3. Convert lat/lon to ECEF Cartesian coordinates and build KD-tree ----
# Visual locations (lat, lng)
vis_lats = visual_features_per_loc['lat'].values
vis_lons = visual_features_per_loc['lng'].values
visual_ecef = latlon_to_ecef(vis_lats, vis_lons)  # in meters

# Collision locations (latitude, longitude) - adapt column names if different
if not {'latitude', 'longitude'}.issubset(collision_df.columns):
    raise KeyError("collision_df must contain 'latitude' and 'longitude' columns")

col_lats = collision_df['latitude'].values
col_lons = collision_df['longitude'].values
collision_ecef = latlon_to_ecef(col_lats, col_lons)  # in meters

# Build spatial index on Cartesian coordinates (meters)
tree = cKDTree(visual_ecef)

# Find the nearest visual feature for every accident (no distance upper bound)
# distances returned are Euclidean meters (since ECEF is in meters)
distances_m, indices = tree.query(collision_ecef, k=1)

# ---- 4. Merge Data (match every collision to its nearest visual feature) ----
# Prepare feature columns from visual_features_per_loc
feature_cols = visual_features_per_loc.columns.drop(['lat', 'lng'])

# Create DataFrame of matched visual features for each collision using the indices
# Note: indices is an array of integers with length == len(collision_df)
matched_visual_rows = visual_features_per_loc.iloc[indices][feature_cols].reset_index(drop=True)

# Prepare final enriched dataframe by concatenating matched features and the distance column
features_to_add = matched_visual_rows.set_index(collision_df.index)
enriched_df = pd.concat([collision_df.reset_index(drop=True), features_to_add], axis=1)
enriched_df['distance_from_point'] = distances_m  # meters

# ---- 5. Reporting ----
total_collisions = len(collision_df)
matched_count = total_collisions  # we matched every collision to nearest visual point
matched_pct = 100.0

print(f"Total collisions (input): {total_collisions}")
print(f"Matched with features: {matched_count} ({matched_pct:.2f}%)")
print("Distance units: meters (ECEF Euclidean distance).")

# ---- 6. Severity detection + statistics (same logic as original) ----
matched_df = enriched_df.copy()  # all rows are matched

# --- Identify the severity column automatically (common names) ---
severity_candidates = [
    'accident_severity', 'severity', 'Accident_Severity', 'severity_label',
    'acc_sev', 'severity_code', 'severity_type'
]
severity_col = None
# prefer exact matches first
for c in severity_candidates:
    if c in matched_df.columns:
        severity_col = c
        break

# fallback: look for a column containing 'sever' or 'accident' in its name
if severity_col is None:
    for c in matched_df.columns:
        if 'sever' in c.lower() or 'accident' in c.lower():
            severity_col = c
            break

# If still None, we won't compute severity stats (but will save CSV)
if severity_col is None:
    print("Warning: Could not automatically find a severity column in the matched data.")
    print("Available columns (sample):", list(matched_df.columns[:30]))
    matched_df.to_csv('enriched_collision_data_with_distance_no_severity.csv', index=False)
    print("Saved matched data to 'enriched_collision_data_with_distance_no_severity.csv'.")
else:
    print(f"Detected severity column: '{severity_col}'")

    # Normalize / map severity to canonical labels: 'Fatal', 'Serious', 'Slight'
    sev_series = matched_df[severity_col]

    def normalize_severity(s):
        if pd.isna(s):
            return np.nan
        if isinstance(s, (int, np.integer, float, np.floating)):
            try:
                si = int(s)
                if si == 1:
                    return 'Fatal'
                elif si == 2:
                    return 'Serious'
                elif si == 3:
                    return 'Slight'
            except Exception:
                pass
        s_str = str(s).strip().lower()
        if 'fatal' in s_str or s_str == '1':
            return 'Fatal'
        if 'serious' in s_str or 'serious-injury' in s_str or s_str == '2':
            return 'Serious'
        if 'slight' in s_str or 'minor' in s_str or s_str == '3':
            return 'Slight'
        return s_str

    matched_df['accident_severity_normalized'] = sev_series.map(normalize_severity)

    # Count canonical categories (ensure the requested order)
    categories = ['Fatal', 'Serious', 'Slight']
    counts = matched_df['accident_severity_normalized'].value_counts(dropna=False)

    fatal_count = int(counts.get('Fatal', 0))
    serious_count = int(counts.get('Serious', 0))
    slight_count = int(counts.get('Slight', 0))

    def pct(n):
        return (n / matched_count * 100.0) if matched_count > 0 else 0.0

    fatal_pct = pct(fatal_count)
    serious_pct = pct(serious_count)
    slight_pct = pct(slight_count)

    print("\nMatched set severity breakdown (counts and % of matched set):")
    print(f"  Fatal:   {fatal_count} ({fatal_pct:.2f}%)")
    print(f"  Serious: {serious_count} ({serious_pct:.2f}%)")
    print(f"  Slight:  {slight_count} ({slight_pct:.2f}%)")

    other_labels = [lab for lab in counts.index if lab not in categories and pd.notna(lab)]
    if other_labels:
        print("\nOther / unrecognized severity labels present in matched data (counts):")
        for lab in other_labels:
            print(f"  {lab}: {int(counts[lab])}")
    cols = [c for c in matched_df.columns if c.startswith('obj_') or c.startswith('seg_')]
    if cols:
        matched_df.loc[:, cols] = matched_df.loc[:, cols].fillna(0)
    matched_df = matched_df.drop(columns=['accident_severity_normalized'], errors='ignore')
    if severity_col in matched_df.columns:
      cols = [c for c in matched_df.columns if c != severity_col] + [severity_col]
      matched_df = matched_df[cols]

    obj_prob_cols = sorted(
        [c for c in matched_df.columns if c.startswith('obj_') and not c.endswith('_count')]
    )

    new_order = []
    used = set()

    for col in matched_df.columns:
        if col in used:
            continue

        if col in obj_prob_cols:
            count_col = f"{col}_count"
            new_order.append(col)
            used.add(col)

            if count_col in matched_df.columns:
                new_order.append(count_col)
                used.add(count_col)
        else:
            if col not in used:
                new_order.append(col)
                used.add(col)

    matched_df = matched_df[new_order]
    # Save matched results (includes distance_from_point in meters)
    matched_df.to_csv('enriched_collision_data_with_distance.csv', index=False)
    print("\nSaved matched data to 'enriched_collision_data_with_distance.csv'.")
