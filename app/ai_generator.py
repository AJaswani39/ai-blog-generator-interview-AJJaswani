import os
from dotenv import load_dotenv
from openai import OpenAI

from app.seo_fetcher import get_search_volume, get_avg_cpc, get_keyword_difficulty

def generate_blog_post(topic, keywords):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    
    prompt = f"Write a blog post about {topic} using the following keywords: {', '.join(keywords)}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Updated model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.5,
    )
    
    return response.choices[0].message.content

def generate_blog_title(topic):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    
    prompt = f"Generate a title for a blog post about {topic}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Updated model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=64,
        temperature=0.5,
    )
    
    return response.choices[0].message.content



