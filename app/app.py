# Importing the necessary modules and functions
from flask import Flask

app = Flask(__name__)

from app.ai_generator import generate_blog_post, generate_blog_title
from app.seo_fetcher import get_search_volume, get_avg_cpc, get_keyword_difficulty

@app.route('/')
def main():
    blog_title = generate_blog_title("AI")
    blog_post = generate_blog_post("AI", ["AI", "Artificial Intelligence"])
    search_volume_ai = get_search_volume("AI")
    avg_cpc_ai = get_avg_cpc("AI")
    keyword_difficulty_ai = get_keyword_difficulty("AI")
    search_volume = get_search_volume("Artificial Intelligence")
    return f"""
        <h1>{blog_title}</h1>
        <p>{blog_post}</p>
        <p>Search Volume for {blog_title}: {search_volume_ai}</p>
        <p>Avg CPC for {blog_title}: {avg_cpc_ai}</p>
        <p>Keyword Difficulty for {blog_title}: {keyword_difficulty_ai}</p>
        <p>Search Volume for {blog_title}: {search_volume}</p>
    """

@app.route('/about')
def about():
    return "<h1>About This Blog Generator</h1><p>This application uses AI to generate blog content.</p>"
