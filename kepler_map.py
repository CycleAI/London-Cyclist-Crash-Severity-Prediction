# kepler_map.py
!pip install keplergl pandas
from keplergl import KeplerGl
import pandas as pd

CSV_PATH = "greater_london_grid_50m_full.csv"
OUTPUT_HTML = "london_kepler_map.html"

df = pd.read_csv(CSV_PATH)

map_1 = KeplerGl(height=800)
map_1.add_data(data=df, name="london_points")

config = {
    "version": "v1",
    "config": {
        "visState": {},
        "mapState": {
            "latitude": 51.5073509,   # London center latitude
            "longitude": -0.1277583,  # London center longitude
            "zoom": 11,               # starting zoom level
            "pitch": 0,
            "bearing": 0
        },
        "mapStyle": {}
    }
}
map_1.save_to_html(file_name=OUTPUT_HTML, config=config)
print("Saved kepler map to", OUTPUT_HTML)
