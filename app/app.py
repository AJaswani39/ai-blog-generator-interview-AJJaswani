# Importing the necessary modules and functions
import os
import atexit
import sys
import re
import random
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler
from functools import lru_cache
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import functions before creating app
from app.ai_generator import generate_blog_post, generate_blog_title, DEVELOPMENT_MODE, generate_content_batch, generate_seo_metrics
from app.seo_fetcher import get_search_volume, get_avg_cpc, get_keyword_difficulty

# Print development mode status at app startup
print(f"App starting with DEVELOPMENT_MODE = {DEVELOPMENT_MODE}")

PREDEFINED_KEYWORDS = [
    "wireless earbuds",
    "smart home devices",
    "AI in healthcare",
    "electric vehicles",
    "blockchain technology",
    "remote work tools",
    "fitness trackers",
    "sustainable fashion",
    "cloud computing",
    "virtual reality"
]

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'flask_cache'})
limiter = Limiter(get_remote_address, app=app, default_limits=["60 per hour"])

# Base HTML template for consistent styling
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .metrics { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .error { color: red; }
        nav { margin-bottom: 20px; }
        nav a { margin-right: 15px; }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/generate?keyword=AI">Generate Blog</a>
    </nav>
    <div class="content">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# Define blog storage directory
BLOG_DIR = os.path.join(os.getcwd(), 'blogs')
os.makedirs(BLOG_DIR, exist_ok=True)

# Scheduler function (moved outside of scheduler() function)
def generate_and_save(topic, keywords):
    try:
        # Generate blog content and SEO metrics
        content = generate_content_batch(topic, keywords)
        metrics = generate_seo_metrics(topic)

        # Render HTML output
        html_output = render_template_string(
            BASE_TEMPLATE,
            title=content["title"],
            content=content["content"]
        )

        # Save HTML output to a safe file in a dedicated directory
        safe_name = safe_filename(topic)
        save_dir = "saved_blogs"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"blog_{safe_name}_{timestamp}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_output)

        print(f"Blog saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error in scheduled task: {e}")
        return None

# Initialize scheduler only in production mode
if not DEVELOPMENT_MODE:
    scheduler = BackgroundScheduler()
    def scheduled_job():
        topic = random.choice(PREDEFINED_KEYWORDS)
        generate_and_save(topic, [topic])
    # Run every day at 12:00 AM server time - or any other time you prefer - just edit the hour and minute. 
    # Hours go from 0 to 23, minutes from 0 to 59.
    print("Scheduler initialized for daily blog generation.")
    scheduler.add_job(
        scheduled_job,
        'cron',
        hour=0,
        minute=0
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def main():
    try:
        # Use cached or mock data for the homepage example
        if DEVELOPMENT_MODE:
            blog_title = "The Ultimate Guide to AI"
            blog_post = "This is a sample blog post about AI and Artificial Intelligence. It demonstrates how the application works without making API calls."
        else:
            # Only make API calls in production
            blog_title = generate_blog_title("AI")
            blog_post = generate_blog_post("AI", ["AI", "Artificial Intelligence"])
        
        # SEO data doesn't use the API, so it's fine to call
        search_volume_ai = cached_get_search_volume("AI")
        avg_cpc_ai = cached_get_avg_cpc("AI")
        keyword_difficulty_ai = cached_get_keyword_difficulty("AI")
        search_volume = cached_get_search_volume("Artificial Intelligence")
        
        content = f"""
            <h1>{blog_title}</h1>
            <p>{blog_post}</p>
            <div class="metrics">
                <h2>SEO Metrics</h2>
                <p>Search Volume for AI: {search_volume_ai}</p>
                <p>Avg CPC for AI: ${avg_cpc_ai}</p>
                <p>Keyword Difficulty for AI: {keyword_difficulty_ai}/100</p>
                <p>Search Volume for Artificial Intelligence: {search_volume}</p>
            </div>
        """
        
        return render_template_string(BASE_TEMPLATE, title="AI Blog Generator", content=content)
    except Exception as e:
        return render_template_string(BASE_TEMPLATE, 
            title="Error", 
            content=f"<div class='error'><h1>Error</h1><p>{str(e)}</p></div>")

@app.route('/about')
def about():
    content = """
        <h1>About This Blog Generator</h1>
        <p>This application uses AI to generate blog content based on keywords and topics.</p>
        <p>It leverages OpenAI's GPT models to create engaging and informative blog posts.</p>
        <p>The application also provides SEO metrics to help optimize content for search engines.</p>
    """
    return render_template_string(BASE_TEMPLATE, title="About", content=content)

@app.route('/api/seo', methods=['GET'])
def get_seo_data():
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({"error": "Keyword parameter is required"}), 400
        
        data = {
            'keyword': keyword,
            'search_volume': cached_get_search_volume(keyword),
            'avg_cpc': cached_get_avg_cpc(keyword),
            'keyword_difficulty': cached_get_keyword_difficulty(keyword)
        }

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10 per hour")
def generate_blog():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must include JSON data"}), 400
            
        topic = data.get('topic')
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
            
        keywords = data.get('keywords', [topic])
        
        # Generate content
        blog_title = generate_blog_title(topic)
        blog_post = generate_blog_post(topic, keywords)

        return jsonify({
            'title': blog_title,
            'content': blog_post
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def safe_filename(keyword):
    # Only allow alphanumeric, dash, and underscore
    return re.sub(r'[^a-zA-Z0-9_-]', '_', keyword)

@app.route('/generate', methods=['GET'])
@limiter.limit("10 per hour")
def generate_blog_from_keyword():
    try:
        keyword = request.args.get('keyword', 'AI')
        print(f"generate_blog_from_keyword called with DEVELOPMENT_MODE = {DEVELOPMENT_MODE}")

        # Generate content and SEO metrics
        content = generate_content_batch(keyword, [keyword])
        metrics = generate_seo_metrics(keyword)

        # Render HTML output
        html_output = render_template_string(
            BASE_TEMPLATE,
            title=content["title"],
            content=content["content"]
        )

        # Save HTML output to a safe file in a dedicated directory
        safe_name = safe_filename(keyword)
        save_dir = "saved_blogs"
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"blog_{safe_name}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_output)

        # Return JSON result (content + metrics)
        return jsonify({
            "title": content["title"],
            "content": content["content"],
            "seo_metrics": metrics
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug')
def debug_info():
    """Route to check configuration and settings"""
    from app.ai_generator import DEVELOPMENT_MODE, check_api_key
    
    # Check API key
    api_key_valid = check_api_key()
    
    # Get environment variables
    env_vars = {k: v for k, v in os.environ.items() if k.startswith('OPEN')}
    # Mask API keys for security
    for k, v in env_vars.items():
        if 'API_KEY' in k and v:
            env_vars[k] = v[:4] + '...' + v[-4:] if len(v) > 8 else '***'
    
    content = f"""
        <h1>Debug Information</h1>
        <h2>Configuration</h2>
        <ul>
            <li>Development Mode: {DEVELOPMENT_MODE}</li>
            <li>API Key Valid: {api_key_valid}</li>
            <li>Python Version: {sys.version}</li>
        </ul>
        
        <h2>Environment Variables</h2>
        <ul>
            {''.join([f'<li>{k}: {v}</li>' for k, v in env_vars.items()])}
        </ul>
    """
    
    return render_template_string(BASE_TEMPLATE, title="Debug Info", content=content)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    content = """
        <div class='error'>
            <h1>Page Not Found</h1>
            <p>The requested page does not exist.</p>
        </div>
    """
    return render_template_string(BASE_TEMPLATE, title="Not Found", content=content), 404

@app.errorhandler(500)
def server_error(e):
    content = """
        <div class='error'>
            <h1>Server Error</h1>
            <p>An internal server error occurred. Please try again later.</p>
        </div>
    """
    return render_template_string(BASE_TEMPLATE, title="Error", content=content), 500

@lru_cache(maxsize=128)
def cached_get_search_volume(keyword):
    return get_search_volume(keyword)

@lru_cache(maxsize=128)
def cached_get_avg_cpc(keyword):
    return get_avg_cpc(keyword)

@lru_cache(maxsize=128)
def cached_get_keyword_difficulty(keyword):
    return get_keyword_difficulty(keyword)
