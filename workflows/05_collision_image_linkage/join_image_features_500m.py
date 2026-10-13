"""
Collision–Image Feature Matching Pipeline

This script enriches road collision records with visual and environmental
features extracted from nearby street-level imagery.

Pipeline overview:
1. Load collision, image metadata, and extracted visual feature datasets.
2. Associate each image's visual features with its geographic coordinates.
3. Aggregate the four image orientations captured at each location into a
   single feature vector.
4. Build a spatial index (KD-tree) for efficient nearest-neighbor searches.
5. Match each collision to the nearest image location within a 500 m radius.
6. Merge the matched visual features into the collision dataset.
7. Report matching statistics and summarize accident severity for matched
   collisions.
8. Export the enriched collision dataset containing only successfully
   matched collision records.

The resulting dataset combines accident information with semantic
segmentation, object detection, and image-level statistics for use in
downstream statistical analysis and machine learning.

Dependencies:
- pandas
- numpy
- scipy (cKDTree)
"""
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


# 1. Load the datasets
collision_df = pd.read_csv('final_mapped_accidents.csv')
collision_df = collision_df.drop(columns=['year'])
mapping_df = pd.read_csv('metadata_images_mapping.csv')
features_df = pd.read_csv('processed_features_conf_0.5_probs.csv')

# Clean missing values
mapping_df = mapping_df.dropna(subset=['image_blob_name', 'lat', 'lng'])
features_df = features_df.dropna(subset=['image_name'])
features_df = features_df.fillna(0)
# 2. Link Features to Coordinates
# Extract the base filename (e.g., '4411_0.jpg') from the full blob path
mapping_df['image_filename'] = mapping_df['image_blob_name'].astype(str).apply(lambda x: x.split('/')[-1])

# Merge visual features with their lat/lng coordinates
visual_data = pd.merge(
    features_df,
    mapping_df[['image_filename', 'lat', 'lng', 'year']],
    left_on='image_name',
    right_on='image_filename',
    how='inner'
)

# Average the features for the 4 image angles at each unique location
visual_features_per_loc = visual_data.drop(columns=['image_name', 'image_filename']).groupby(['lat', 'lng']).mean().reset_index()

# 3. Spatial Search (100m Radius)
# We scale Longitude by cos(Lat) to approximate Euclidean distance in meters
# If your study area isn't London, change mean_lat accordingly.
mean_lat = np.radians(51.5)  # Approximate latitude for London
lng_scale = np.cos(mean_lat)

visual_coords = visual_features_per_loc[['lat', 'lng']].values
visual_coords_scaled = visual_coords.copy()
visual_coords_scaled[:, 1] *= lng_scale

collision_coords = collision_df[['latitude', 'longitude']].values
collision_coords_scaled = collision_coords.copy()
collision_coords_scaled[:, 1] *= lng_scale

# Build spatial index
tree = cKDTree(visual_coords_scaled)

# 500 meters expressed in degrees latitude
radius_deg = 500 / 111320.0

# Find the nearest visual features within 500m for every accident
distances, indices = tree.query(collision_coords_scaled, distance_upper_bound=radius_deg)

# 4. Merge Data (only keep matched points)
matched_mask = indices < len(visual_features_per_loc)
feature_cols = visual_features_per_loc.columns.drop(['lat', 'lng'])

# Prepare empty columns for features
matched_feature_values = np.full((len(collision_df), len(feature_cols)), np.nan)

# Fill rows where a match was found
if matched_mask.any():
    matched_feature_values[matched_mask] = visual_features_per_loc.iloc[indices[matched_mask]][feature_cols].values

# Create final DataFrame (enriched)
features_to_add = pd.DataFrame(matched_feature_values, columns=feature_cols, index=collision_df.index)
enriched_df = pd.concat([collision_df, features_to_add], axis=1)

total_collisions = len(collision_df)
matched_count = int(matched_mask.sum())
matched_pct = matched_mask.mean() * 100.0

print(f"Total collisions (input): {total_collisions}")
print(f"Matched with features: {matched_count} ({matched_pct:.2f}%)")

# Only keep matched rows for final CSV (user requested: don't include unmatched points)
if matched_count == 0:
    print("No collisions were matched to visual features within 500m. No output CSV will be written.")
else:
    matched_df = enriched_df.loc[matched_mask].copy()  # only rows that had a match

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
        # Save matched only
        matched_df.to_csv('enriched_collision_data_500m_bad.csv', index=False)
        print("Saved matched data to 'enriched_collision_data_500m_bad.csv' (no severity stats).")
    else:
        print(f"Detected severity column: '{severity_col}'")

        # Normalize / map severity to canonical labels: 'Fatal', 'Serious', 'Slight'
        sev_series = matched_df[severity_col]

        def normalize_severity(s):
            # handle numeric encodings (common: 1=Fatal,2=Serious,3=Slight)
            if pd.isna(s):
                return np.nan
            # numeric-like
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
            # strings: check keywords
            s_str = str(s).strip().lower()
            if 'fatal' in s_str or s_str == '1':
                return 'Fatal'
            if 'serious' in s_str or 'serious-injury' in s_str or s_str == '2':
                return 'Serious'
            if 'slight' in s_str or 'minor' in s_str or s_str == '3':
                return 'Slight'
            # other common encodings: "KSI" or "S" etc are ambiguous; return raw
            return s_str  # leave as-is for later counting

        matched_df['accident_severity_normalized'] = sev_series.map(normalize_severity)

        # Count canonical categories (ensure the requested order)
        categories = ['Fatal', 'Serious', 'Slight']
        counts = matched_df['accident_severity_normalized'].value_counts(dropna=False)

        # Safely get counts for our three categories (0 if missing)
        fatal_count = int(counts.get('Fatal', 0))
        serious_count = int(counts.get('Serious', 0))
        slight_count = int(counts.get('Slight', 0))

        # Percentages relative to matched_count
        def pct(n):
            return (n / matched_count * 100.0) if matched_count > 0 else 0.0

        fatal_pct = pct(fatal_count)
        serious_pct = pct(serious_count)
        slight_pct = pct(slight_count)

        print("\nMatched set severity breakdown (counts and % of matched set):")
        print(f"  Fatal:   {fatal_count} ({fatal_pct:.2f}%)")
        print(f"  Serious: {serious_count} ({serious_pct:.2f}%)")
        print(f"  Slight:  {slight_count} ({slight_pct:.2f}%)")

        # Optionally: show any other (unexpected) severity labels found
        other_labels = [lab for lab in counts.index if lab not in categories and pd.notna(lab)]
        if other_labels:
            print("\nOther / unrecognized severity labels present in matched data (counts):")
            for lab in other_labels:
                print(f"  {lab}: {int(counts[lab])}")
        matched_df.rename(columns={'year': 'infrastructure_year'})

        # Save matched only (drop rows where no match)
        # Keep the normalized severity column so you can inspect later
        matched_df.to_csv('enriched_collision_data_500m_new.csv', index=False)
        print("\nSaved matched data to 'enriched_collision_data_500m_new.csv'.")
