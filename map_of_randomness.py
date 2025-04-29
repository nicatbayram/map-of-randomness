import requests
import random
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen
import time
import argparse
import webbrowser
from tqdm import tqdm

class HistoricalEventsMapper:
    def __init__(self, config_file=None):
        # Get today's date or use provided date
        self.today = datetime.now()
        self.month = self.today.strftime("%B")
        self.day = self.today.day
        
        # Default configuration
        self.config = {
            "output_path": os.path.join(os.path.expanduser("~"), "Desktop", "wiki", "map_of_randomness.html"),
            "max_events": 10,
            "auto_open": True,
            "language": "en",
            "use_marker_cluster": True,
            "use_heatmap": False,
            "cache_locations": True
        }
        
        # Load config from file if provided
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception as e:
                print(f"[!] Error loading configuration file: {e}")
        
        # Create cache directory if it doesn't exist
        self.cache_dir = os.path.join(os.path.dirname(self.config["output_path"]), "cache")
        if self.config["cache_locations"] and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        
        # Location cache
        self.location_cache = {}
        self.load_location_cache()
        
        # Initialize geolocator
        self.geolocator = Nominatim(user_agent="map_of_randomness")

    def load_location_cache(self):
        """Load location cache from file"""
        cache_file = os.path.join(self.cache_dir, "location_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.location_cache = json.load(f)
                print(f"[✓] {len(self.location_cache)} location cache loaded")
            except Exception as e:
                print(f"[!] Error loading location cache: {e}")

    def save_location_cache(self):
        """Save location cache to file"""
        if self.config["cache_locations"]:
            cache_file = os.path.join(self.cache_dir, "location_cache.json")
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.location_cache, f, ensure_ascii=False, indent=2)
                print(f"[✓] Location cache saved: {len(self.location_cache)} entries")
            except Exception as e:
                print(f"[!] Error saving location cache: {e}")

    def set_date(self, month=None, day=None):
        """Set a specific date instead of today"""
        if month:
            self.month = month
        if day:
            self.day = int(day)
        return self

    def fetch_random_wikipedia_events(self):
        """Fetch random historical events from Wikipedia"""
        lang_prefix = self.config["language"]
        if lang_prefix == "en":
            url = f"https://en.wikipedia.org/wiki/Wikipedia:Selected_anniversaries/{self.month}_{self.day}"
        else:
            # Different languages or URL structures can be used
            url = f"https://{lang_prefix}.wikipedia.org/wiki/Wikipedia:Selected_anniversaries/{self.month}_{self.day}"
            
        print(f"[+] Fetching data from Wikipedia: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Error check
            
            soup = BeautifulSoup(response.text, "html.parser")
            events = []
            
            for li in soup.select("ul > li"):
                text = li.get_text()
                links = li.find_all("a", href=True)
                
                event_info = {"text": text, "links": []}
                
                for link in links:
                    if link['href'].startswith("/wiki/") and ":" not in link['href']:
                        title = link.get('title') or link.get_text()
                        wiki_url = f"https://{lang_prefix}.wikipedia.org{link['href']}"
                        event_info["links"].append({
                            "title": title,
                            "url": wiki_url
                        })
                
                if event_info["links"]:
                    event_info["title"] = event_info["links"][0]["title"]
                    event_info["url"] = event_info["links"][0]["url"]
                    events.append(event_info)
            
            # Select random events up to the maximum limit
            if events:
                return random.sample(events, min(self.config["max_events"], len(events)))
            else:
                print("[!] No events found")
                return []
                
        except Exception as e:
            print(f"[!] Error fetching Wikipedia data: {e}")
            return []

    def geolocate_event(self, event_text):
        """Geolocate the event using location keywords"""
        places_to_try = [p.strip() for p in event_text.split(",") if len(p.strip()) > 3]
        
        for place in places_to_try:
            # Check the cache
            if place in self.location_cache:
                coords = self.location_cache[place]
                print(f"[✓] Location found in cache: {place} → {coords}")
                return coords
            
            try:
                location = self.geolocator.geocode(place, timeout=10)
                if location:
                    coords = (location.latitude, location.longitude)
                    print(f"[✓] Location found: {place} → {coords}")
                    # Add to cache
                    self.location_cache[place] = coords
                    return coords
            except Exception as e:
                print(f"[!] Error: {e}")
            
            time.sleep(1)  # Sleep for API rate limiting
        
        return None

    def create_map(self, events):
        """Create the interactive map with events"""
        # Map center and zoom level
        map_obj = folium.Map(location=[20, 0], zoom_start=2)
        
        # Add fullscreen control
        Fullscreen().add_to(map_obj)
        
        # Use marker cluster
        if self.config["use_marker_cluster"]:
            marker_cluster = MarkerCluster().add_to(map_obj)
        
        # Heatmap data
        heat_data = []
        
        print("[*] Finding locations for events...")
        for event in tqdm(events):
            coords = self.geolocate_event(event["text"])
            if coords:
                # Create rich content with links
                links_html = "<br>".join([f"<a href='{link['url']}' target='_blank'>{link['title']}</a>" 
                                         for link in event.get("links", [])])
                
                popup_content = f"""
                <div style="max-width:300px">
                    <h4>{event.get('title', 'Historical Event')}</h4>
                    <p>{event['text']}</p>
                    <h5>Related Links:</h5>
                    {links_html}
                </div>
                """
                
                # Add marker
                if self.config["use_marker_cluster"]:
                    folium.Marker(
                        location=coords,
                        tooltip=event.get('title', 'Click'),
                        popup=folium.Popup(popup_content, max_width=300)
                    ).add_to(marker_cluster)
                else:
                    folium.Marker(
                        location=coords,
                        tooltip=event.get('title', 'Click'),
                        popup=folium.Popup(popup_content, max_width=300)
                    ).add_to(map_obj)
                
                # Add heatmap data
                heat_data.append([coords[0], coords[1], 1.0])
        
        # Create heatmap (optional)
        if self.config["use_heatmap"] and heat_data:
            HeatMap(heat_data).add_to(map_obj)
        
        # Add map title
        map_title = f"Historical Events of {self.month} {self.day}"
        map_obj.get_root().html.add_child(folium.Element(f"""
        <div style="position:fixed; bottom:10px; left:10px; z-index:1000; background-color:white; 
                    padding:10px; border-radius:5px; box-shadow:0 0 5px gray;">
            <h3>{map_title}</h3>
            <p>This map shows important events that happened on this day in history.</p>
        </div>
        """))
        
        return map_obj

    def run(self):
        """Run the main process"""
        print("[*] Fetching random events...")
        events = self.fetch_random_wikipedia_events()
        
        if not events:
            print("[!] No events to process.")
            return False
            
        print(f"[*] {len(events)} events fetched. Creating map...")
        map_obj = self.create_map(events)
        
        # Create output folder
        os.makedirs(os.path.dirname(self.config["output_path"]), exist_ok=True)
        
        # Save the map
        map_obj.save(self.config["output_path"])
        print(f"[✓] Map created successfully! File saved at: {self.config['output_path']}")
        
        # Save location cache
        self.save_location_cache()
        
        # Open automatically?
        if self.config["auto_open"]:
            webbrowser.open(f"file://{os.path.abspath(self.config['output_path'])}")
        
        return True


def parse_arguments():
    """Process command line arguments"""
    parser = argparse.ArgumentParser(description="Historical Events Map Generator")
    parser.add_argument("--month", help="Month name (English, e.g., January)")
    parser.add_argument("--day", help="Day (1-31)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Path to output HTML file")
    parser.add_argument("--max-events", type=int, help="Maximum number of events")
    parser.add_argument("--language", default="en", help="Wikipedia language (e.g., tr, en, de)")
    parser.add_argument("--no-cluster", action="store_true", help="Do not use marker clustering")
    parser.add_argument("--heatmap", action="store_true", help="Add heatmap")
    parser.add_argument("--no-open", action="store_true", help="Do not open the map after creation")
    return parser.parse_args()


if __name__ == "__main__":
    # Get command line arguments
    args = parse_arguments()
    
    # Initialize map generator
    mapper = HistoricalEventsMapper(config_file=args.config)
    
    # Update configuration from command line arguments
    if args.output:
        mapper.config["output_path"] = args.output
    if args.max_events:
        mapper.config["max_events"] = args.max_events
    if args.language:
        mapper.config["language"] = args.language
    if args.no_cluster:
        mapper.config["use_marker_cluster"] = False
    if args.heatmap:
        mapper.config["use_heatmap"] = True
    if args.no_open:
        mapper.config["auto_open"] = False
    
    # Set specific date (if any)
    if args.month or args.day:
        mapper.set_date(args.month, args.day)
    
    # Run
    mapper.run()
