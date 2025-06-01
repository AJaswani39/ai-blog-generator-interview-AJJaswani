import requests
import os
import random
from dotenv import load_dotenv
load_dotenv()

# Predefined data for common keywords
mock_data = {
    "AI": {"search_volume": 10000, "avg_cpc": 1.5, "keyword_difficulty": 75},
    "Machine Learning": {"search_volume": 5500, "avg_cpc": 2.1, "keyword_difficulty": 65},
    "Artificial Intelligence": {"search_volume": 7000, "avg_cpc": 1.8, "keyword_difficulty": 70},
    "Deep Learning": {"search_volume": 3000, "avg_cpc": 2.5, "keyword_difficulty": 80},
    "Natural Language Processing": {"search_volume": 2500, "avg_cpc": 2.2, "keyword_difficulty": 75},
    "Computer Vision": {"search_volume": 1800, "avg_cpc": 2.8, "keyword_difficulty": 85},
    "Robotics": {"search_volume": 1200, "avg_cpc": 3.0, "keyword_difficulty": 90},
    "Internet of Things": {"search_volume": 2000, "avg_cpc": 2.3, "keyword_difficulty": 72},
    "Big Data": {"search_volume": 3500, "avg_cpc": 2.0, "keyword_difficulty": 68},
    "Blockchain": {"search_volume": 1500, "avg_cpc": 2.7, "keyword_difficulty": 82}
}

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
    
