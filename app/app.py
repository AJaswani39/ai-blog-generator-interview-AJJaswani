# Importing the necessary modules and functions
import os
from datetime import datetime
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

from app.ai_generator import generate_blog_post, generate_blog_title
from app.seo_fetcher import get_search_volume, get_avg_cpc, get_keyword_difficulty

@app.route('/')
def main():
    # Generate the blog post - an example.
    blog_title = generate_blog_title("AI")
    blog_post = generate_blog_post("AI", ["AI", "Artificial Intelligence"])
    # Get SEO data for the blog post.
    search_volume_ai = get_search_volume("AI")
    avg_cpc_ai = get_avg_cpc("AI")
    keyword_difficulty_ai = get_keyword_difficulty("AI")
    search_volume = get_search_volume("Artificial Intelligence")
    # Return the generated blog post and SEO data.
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

def scheduler():
    def generate_and_save(topic, keywords):
        # Generate blog content
        blog_title = generate_blog_title(topic)
        blog_post = generate_blog_post(topic, keywords)
        
        # Create blogs directory if it doesn't exist
        os.makedirs('blogs', exist_ok=True)
        
        # Format filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blogs/blog_{timestamp}.html"
        
        # Write content to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<h1>{blog_title}</h1>\n<p>{blog_post}</p>")
        
        print(f"Blog saved to {filename}")
        return filename
    # This should send a request at least once per day, and should generate for a predefined keyword
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_and_save, 'interval', days=1, args=['AI', ['AI', 'Artificial Intelligence']])
    scheduler.start()
    return

@app.route('/api/seo', methods=['GET'])
def get_seo_data():
    keyword = request.args.get('keyword', 'AI')  # Default to 'AI' if no keyword provided
    
    data = {
        'keyword': keyword,
        'search_volume': get_search_volume(keyword),
        'avg_cpc': get_avg_cpc(keyword),
        'keyword_difficulty': get_keyword_difficulty(keyword)
    }

    return jsonify(data)

@app.route('/api/generate', methods=['POST'])
def generate_blog():
    data = request.get_json()
    topic = data.get('topic', 'AI')
    keywords = data.get('keywords', ["AI", "Artificial Intelligence"])

    blog_title = generate_blog_title(topic)
    blog_post = generate_blog_post(topic, keywords)

    return jsonify({
        'title': blog_title,
        'content': blog_post
    })
@app.route('/api/generate-title', methods=['POST'])
def generate_blog_title_api():
    data = request.get_json()
    topic = data.get('topic', 'AI')

    blog_title = generate_blog_title(topic)

    return jsonify({
        'title': blog_title    
    })

@app.route('/api/generate-post', methods=['POST'])    
def generate_blog_post_api():
    data = request.get_json()
    topic = data.get('topic', 'AI')
    keywords = data.get('keywords', ["AI", "Artificial Intelligence"])

    blog_post = generate_blog_post(topic, keywords)

    return jsonify({
        'content': blog_post
    })

@app.route('/generate', methods=['GET'])
def generate_blog_from_keyword():
    # Get keyword from URL parameter, default to 'AI' if not provided
    keyword = request.args.get('keyword', 'AI')
    
    # Generate blog content
    blog_title = generate_blog_title(keyword)
    blog_post = generate_blog_post(keyword, [keyword])
    
    # Get SEO data
    search_volume = get_search_volume(keyword)
    avg_cpc = get_avg_cpc(keyword)
    keyword_difficulty = get_keyword_difficulty(keyword)
    
    # Return HTML response
    return f"""
        <h1>{blog_title}</h1>
        <p>{blog_post}</p>
        <div class="seo-metrics">
            <h2>SEO Metrics for "{keyword}"</h2>
            <p>Search Volume: {search_volume}</p>
            <p>Average CPC: ${avg_cpc}</p>
            <p>Keyword Difficulty: {keyword_difficulty}/100</p>
        </div>
    """
