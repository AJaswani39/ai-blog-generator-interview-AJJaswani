# Importing the necessary modules and functions
from flask import Flask, jsonify, request


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
