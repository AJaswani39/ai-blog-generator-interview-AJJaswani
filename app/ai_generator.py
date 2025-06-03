import os
import time
import random
import functools
import re  # Add this for regex pattern matching
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import logging
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set to False to use the API. True to use mock data.
DEVELOPMENT_MODE = False

# Simple in-memory cache
_cache = {}

def cached(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from function name and arguments
        key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        
        # Return cached result if available
        if key in _cache:
            logger.info(f"Using cached result for {func.__name__}")
            return _cache[key]
        
        # Call the function and cache the result
        result = func(*args, **kwargs)
        _cache[key] = result
        return result
    
    return wrapper

def retry_with_exponential_backoff(
    initial_delay=1, 
    exponential_base=2, 
    jitter=True,
    max_retries=3  # Reduced from 5 to 3
):
    """Retry a function with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize variables
            num_retries = 0
            delay = initial_delay

            # Loop until a successful response or max_retries is hit
            while True:
                try:
                    return func(*args, **kwargs)

                # Retry on rate limit error
                except RateLimitError as e:
                    # Increment retries
                    num_retries += 1
                    logger.warning(f"Rate limit exceeded ({num_retries}/{max_retries}): {str(e)}")
                    
                    # Check if max retries reached
                    if num_retries > max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded. Falling back to mock data.")
                        # Force development mode for this response
                        global DEVELOPMENT_MODE
                        old_mode = DEVELOPMENT_MODE
                        DEVELOPMENT_MODE = True
                        try:
                            result = func(*args, **kwargs)
                            return result
                        finally:
                            DEVELOPMENT_MODE = old_mode
                    
                    # Calculate new delay with exponential backoff and optional jitter
                    delay *= exponential_base * (1 + jitter * random.random())
                    logger.info(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                    
                    # Sleep before retrying
                    time.sleep(delay)
                
                # Handle other exceptions
                except Exception as e:
                    logger.error(f"Error: {e}")
                    # Fall back to development mode response
                    if 'topic' in kwargs:
                        topic = kwargs['topic']
                    else:
                        topic = args[0]  # Assume first arg is topic
                    
                    if func.__name__ == 'generate_blog_post':
                        keywords = args[1] if len(args) > 1 else kwargs.get('keywords', [])
                        return f"[API Error] Sample blog post about {topic} with keywords: {', '.join(keywords)}."
                    else:
                        return f"The Ultimate Guide to {topic}"
        return wrapper
    return decorator

def check_api_key():
    """Verify that the API key is properly set"""
    load_dotenv()
    api_key = os.getenv("OPEN_API_KEY")
    if not api_key:
        logger.error("API key not found! Make sure OPEN_API_KEY is set in your .env file")
        return False
    if api_key.startswith("sk-") and len(api_key) > 20:
        logger.info("API key format looks valid")
        return True
    else:
        logger.error(f"API key format looks invalid: {api_key[:5]}...")
        return False

# Call this at module import time
api_key_valid = check_api_key()
if not api_key_valid:
    logger.warning("Forcing DEVELOPMENT_MODE=True due to API key issues")
    DEVELOPMENT_MODE = True

# Force development mode to True - this is the most important line
DEVELOPMENT_MODE = True

# Add debug print to verify this value is being used
print(f"DEVELOPMENT_MODE is set to: {DEVELOPMENT_MODE}")

# Rate limiting implementation
class RateLimiter:
    def __init__(self, calls_per_minute=20):
        self.calls_per_minute = calls_per_minute
        self.interval = 60.0 / calls_per_minute  # seconds between calls
        self.last_call_time = 0
        self.lock = Lock()
    
    def wait_if_needed(self):
        with self.lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.interval:
                sleep_time = self.interval - time_since_last_call
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_call_time = time.time()

# Create a global rate limiter (3 calls per minute is very conservative)
rate_limiter = RateLimiter(calls_per_minute=3)

# Modify the OpenAI client creation to use rate limiting
def get_openai_client():
    load_dotenv()
    api_key = os.getenv("OPEN_API_KEY")
    
    if not api_key:
        logger.error("API key not found")
        raise ValueError("API key not found. Set OPEN_API_KEY in your .env file")
    
    return OpenAI(api_key=api_key)

@cached
@retry_with_exponential_backoff()
def generate_blog_post(topic, keywords):
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: Generating mock blog post for {topic}")
        return f"This is a development mode blog post about {topic}. It discusses various aspects of {topic} and how it relates to {', '.join(keywords)}."
    
    logger.info(f"PRODUCTION MODE: Making API call to generate blog post for {topic}")
    
    # Apply rate limiting before making the API call
    rate_limiter.wait_if_needed()
    
    client = get_openai_client()
    prompt = f"Write a short blog post about {topic}. Include these keywords: {', '.join(keywords)}."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a concise blog writer. Keep responses under 300 words."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )
    
    return response.choices[0].message.content

@cached
@retry_with_exponential_backoff()
def generate_blog_title(topic):
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: Generating mock blog title for {topic}")
        return f"The Complete Guide to {topic}: Everything You Need to Know"
    
    # Apply rate limiting before making the API call
    rate_limiter.wait_if_needed()
    
    client = get_openai_client()
    prompt = f"Create a short, catchy title for a blog about {topic}"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You create short, catchy blog titles."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.7,
    )
    
    return response.choices[0].message.content

def generate_content_batch(topic, keywords):
    if DEVELOPMENT_MODE:
        return {
            "title": f"The Complete Guide to {topic}",
            "content": f"This is a development mode blog post about {topic}. It discusses various aspects of {topic} and how it relates to {', '.join(keywords)}."
        }
    
    # Apply rate limiting before making the API call
    rate_limiter.wait_if_needed()
    
    client = get_openai_client()
    prompt = f"""
    Create a blog post about {topic}. Include these keywords: {', '.join(keywords)}.
    Format your response as:
    TITLE: [Your catchy title here]
    
    CONTENT: [Your blog post content here]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a concise blog writer. Keep responses under 300 words."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )
    
    # Parse the response to extract title and content
    full_text = response.choices[0].message.content
    title_match = re.search(r"TITLE:\s*(.*?)(?:\n\n|\n|$)", full_text)
    content_match = re.search(r"CONTENT:\s*(.*)", full_text, re.DOTALL)
    
    title = title_match.group(1) if title_match else f"Blog about {topic}"
    content = content_match.group(1) if content_match else full_text
    
    return {
        "title": title.strip(),
        "content": content.strip()
    }
