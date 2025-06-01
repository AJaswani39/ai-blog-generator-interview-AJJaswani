import os
from dotenv import load_dotenv
from openai import OpenAI


def generate_blog_post(topic, keywords):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"Write a blog post about {topic} using the following keywords: {', '.join(keywords)}"
    
    response = client.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    return response.choices[0].text.strip()

def generate_blog_title(topic):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"Generate a title for a blog post about {topic}"
    
    response = client.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=64,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    return response.choices[0].text.strip()
