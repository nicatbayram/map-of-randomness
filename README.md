# Historical Events Map Generator

This application fetches random historical events from Wikipedia for a specific date and displays them on an interactive world map. Each event is shown as a marker at the location where the event took place.

## Features

- **Daily Events**: Automatically find events that happened on today's date or select a specific date
- **Interactive Map**: Display events as markers on a world map
- **Marker Clustering**: Automatically group nearby events to reduce clutter
- **Heatmap Option**: Visualize event concentration areas with a heatmap
- **Location Caching**: Save and reuse geocoded locations to improve performance
- **Multilingual Support**: Fetch content from different Wikipedia language versions
- **Configurable**: Use command line arguments or a configuration file
- **Rich Content**: View event details and related Wikipedia links in popups
- **Fullscreen Mode**: Expand the map to fullscreen for better viewing

## Installation

### Prerequisites

Make sure you have Python 3.6+ installed along with these required packages:

```bash
pip install requests beautifulsoup4 geopy folium tqdm
```

### Download

Clone this repository or download the script file:

```bash
git clone https://github.com/nicatbayram/map-of-randomness.git
cd map_of_randomness
```

## Usage

### Basic Usage

Run the script with default settings (today's date, English Wikipedia):

```bash
python map_of_randomness.py
```

The map will be generated at `~/Desktop/wiki/map_of_randomness.html` and automatically opened in your default browser.

### Command Line Options

```bash
python map_of_randomness.py --help
```

Available options:

- `--month`: Month name in English (e.g., "January")
- `--day`: Day number (1-31)
- `--config`: Path to a configuration file
- `--output`: Path for the output HTML file
- `--max-events`: Maximum number of events to display
- `--language`: Wikipedia language code (e.g., en, tr, de, fr)
- `--no-cluster`: Disable marker clustering
- `--heatmap`: Enable heatmap visualization
- `--no-open`: Do not automatically open the map after creation

Examples:

```bash
# Generate map for April 15 with French Wikipedia content
python historical_events_mapper.py --month April --day 15 --language fr

# Generate map with heatmap and 20 events max
python historical_events_mapper.py --heatmap --max-events 20

# Save the map to a specific location and don't open it
python historical_events_mapper.py --output /path/to/my_map.html --no-open
```

### Configuration File

You can create a JSON configuration file to store your preferences:

```json
{
  "output_path": "/path/to/map.html",
  "max_events": 15,
  "auto_open": true,
  "language": "en",
  "use_marker_cluster": true,
  "use_heatmap": false,
  "cache_locations": true
}
```

Then use it with:

```bash
python historical_events_mapper.py --config config.json
```

## How It Works

1. The script fetches the "Selected anniversaries" page from Wikipedia for the specified date
2. It extracts events and their links from the page
3. It attempts to geolocate each event by identifying place names in the text
4. It creates an interactive map with markers at each location
5. Each marker contains detailed information and links to related Wikipedia articles

## Location Caching

The application saves previously geocoded locations to improve performance on subsequent runs. The cache is stored in:

```
[output_folder]/cache/location_cache.json
```

## Customizing the Map

You can modify the script to customize the map appearance:

- Change the base map style by modifying the `folium.Map()` parameters
- Add additional Folium plugins for more features
- Customize marker icons and popup content


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Wikipedia](https://www.wikipedia.org/) for providing historical event data
- [Folium](https://python-visualization.github.io/folium/) for the mapping library
- [GeoPy](https://geopy.readthedocs.io/) for geocoding functionality

## ScreenShots
![111](https://github.com/user-attachments/assets/66390ebc-ca7a-4fe0-9df3-978ba4ba3552)


