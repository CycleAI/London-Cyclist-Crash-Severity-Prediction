# Data

## Crashes used

- Police-recorded cyclist collisions in Greater London (STATS19), January 2013 to June 2025: 59,628 collisions, one row per collision (the most seriously injured cyclist).
- Used for the models: 41,606 collisions from 1 November 2016, when injury-based severity recording began, to 30 June 2025. Of these, 7,678 (18.5%) were serious or fatal.

## Sources

| Information | Source | Licence |
|---|---|---|
| Crashes, road and junction, cyclist age and sex | Police collision records (STATS19) [source to confirm] | [Licence to confirm] |
| Weather before the crash | Open-Meteo Historical Weather API | [Licence to confirm] |
| Schools | Department for Education, Get Information About Schools | [Licence to confirm] |
| Pubs and bars | Food Standards Agency, Food Hygiene Rating Scheme | [Licence to confirm] |
| Bus stops and stations | NaPTAN (Department for Transport); Transport for London station data | [Licence to confirm] |
| Traffic signals | [Source to confirm] | [Licence to confirm] |
| Road network and road distances | Ordnance Survey, OS Open Roads | [Licence to confirm] |
| Deprivation | English indices of deprivation (MHCLG) [edition to confirm] | [Licence to confirm] |
| High streets | Greater London Authority | [Licence to confirm] |
| Road noise | [Source to confirm] | [Licence to confirm] |
| Cyclist counts | [Source to confirm] | [Licence to confirm] |
| Road gradient | OpenStreetMap; Environment Agency LiDAR | [Licence to confirm] |
| Borough boundaries (maps) | London Datastore | [Licence to confirm] |
| Street-level images | Google Street View | Not shared |

## Files in this folder

| File | Content |
|---|---|
| `eligible_pre_crash_inputs.csv` [if shared] | The 41,606 crashes with the 255 eligible inputs, the outcome and the time split |
| `crashes_for_breakdowns.csv` | The 41,606 crashes with the breakdown groups, location, perceived safety score and outcome |

The column meanings are in `results/feature_dictionary.xlsx`. Empty cells are missing values, before filling.

## Not shared

- The raw police files and the intermediate files of notebook 01, which are large and can be rebuilt from the sources.
- The Street View images.
