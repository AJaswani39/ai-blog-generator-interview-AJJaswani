import requests
import os
import json
import random
from dotenv import load_dotenv
load_dotenv()

# Load mock data from JSON file
def load_mock_data():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('app/data', exist_ok=True)
        
        # Check if file exists, if not create it with default data
        if not os.path.exists('app/data/keyword_metrics.json'):
            default_data = {
                "AI": {"search_volume": 10000, "avg_cpc": 1.5, "keyword_difficulty": 75},
                # Add other default keywords...
            }
            with open('app/data/keyword_metrics.json', 'w') as f:
                json.dump(default_data, f, indent=2)
            return default_data
        
        # Load existing data
        with open('app/data/keyword_metrics.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading mock data: {e}")
        return {}

# Load mock data
mock_data = load_mock_data()

def get_search_volume(keyword):
    if keyword in mock_data:
        return mock_data[keyword]["search_volume"]
    else:
        # Generate random but plausible search volume for unknown keywords
        # Shorter keywords tend to have higher search volume
        base_volume = 5000 if len(keyword) < 10 else 2000
        return random.randint(base_volume // 2, base_volume * 2)

def get_avg_cpc(keyword):
    if keyword in mock_data:
        return mock_data[keyword]["avg_cpc"]
    else:
        # Generate random CPC between $0.5 and $5.0
        return round(random.uniform(0.5, 5.0), 2)

def get_keyword_difficulty(keyword):
    if keyword in mock_data:
        return mock_data[keyword]["keyword_difficulty"]
    else:
        # Generate random difficulty score (0-100)
        # Shorter keywords tend to be more competitive
        base_difficulty = 70 if len(keyword) < 10 else 40
        return min(100, max(0, random.randint(base_difficulty - 20, base_difficulty + 20)))
    
