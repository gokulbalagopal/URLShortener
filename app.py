import logging
import traceback
from flask import Flask, request, redirect, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import redis
import string
from urllib.parse import urlparse, urlunparse
from sqlalchemy import desc
import re

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create the Base62 alphabet
BASE62_ALPHABET = string.digits + string.ascii_letters

def base62_encode(num):
    # Implement Base62 encoding
    if num == 0:
        return BASE62_ALPHABET[0]
    
    base62 = []
    while num:
        remainder = num % 62
        base62.append(BASE62_ALPHABET[remainder])
        num //= 62
    
    return ''.join(reversed(base62))

def is_valid_url(url: str) -> bool:
    # Using regular expressions for checking valid URL
    pattern = re.compile(
        r'^(https?://)?'  
        r'([a-zA-Z0-9.-]+)'  
        r'(\.[a-zA-Z]{2,6})'  
        r'(/[\w/-]*)?$'  
    )
    
    # Use the pattern to match the given URL
    return re.match(pattern, url) is not None

# Define the URL model
class URLMapping(db.Model):
    __tablename__ = 'url_mapping'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String, nullable=True, default="")
    created_at = db.Column(db.DateTime, default=datetime.now)  # Using datetime.now
    expires_in = db.Column(db.Integer, nullable=False)

    def __init__(self, long_url, expires_in):
        self.long_url = long_url
        self.expires_in = expires_in

    def generate_short_url(self):
        self.short_url = base62_encode(self.id)
        return self.short_url

# Initialize the database
with app.app_context():
    db.create_all()

# Serve the index HTML page
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Save URL to database and generate short URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    try:
        long_url = request.json.get('long_url')
        expires_in = request.json.get('expires_in', 60)  # Expiration time is 1 minute

        # Check if the URL is empty
        if not long_url:
            return jsonify({"error": "URL is required"}), 400
        parsed_url = urlparse(long_url)

        # Check for valid scheme (http, https, hostname)
        if not parsed_url.scheme:

            long_url = 'http://' + long_url
            parsed_url = urlparse(long_url)
        
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({"error": "Invalid URL format"}), 400


        netloc = parsed_url.netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]

        normalized_url = urlunparse(('http', netloc, parsed_url.path, '', parsed_url.query, ''))

 
        if not is_valid_url(normalized_url):
            return jsonify({"error": "Invalid URL format"}), 400

        existing_mapping = URLMapping.query.filter_by(long_url=normalized_url).order_by(desc(URLMapping.created_at)).first()
        if existing_mapping:
            if datetime.now() <= existing_mapping.created_at + timedelta(seconds=existing_mapping.expires_in):
                return jsonify({"short_url": existing_mapping.short_url})

        url_mapping = URLMapping(long_url=normalized_url, expires_in=expires_in)
        db.session.add(url_mapping)
        db.session.flush() 


        short_url = url_mapping.generate_short_url()
        url_mapping.short_url = short_url
        db.session.commit()  


        redis_client.set(short_url, normalized_url, ex=expires_in)
        
        return jsonify({"short_url": short_url})
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        logging.error(f"Error in shorten_url route: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Redirect to the original URL

@app.route('/<short_url>', methods=['GET'])
def redirect_to_long_url(short_url):
    try:
        # Check cache first
        long_url = redis_client.get(short_url)
        if long_url:
            return redirect(f"{long_url.decode('utf-8')}", code=302)

        # If not in cache, check the database
        url_mapping = URLMapping.query.filter_by(short_url=short_url).first()
        
        if url_mapping:
            # Check if the URL has expired
            if datetime.now() > url_mapping.created_at + timedelta(seconds=url_mapping.expires_in):
                return jsonify({"error": "URL has expired"}), 410

            long_url = url_mapping.long_url

            # Cache the long URL
            redis_client.set(short_url, long_url, ex=url_mapping.expires_in)
            return redirect(f"{long_url}", code=302)

        return jsonify({"error": "URL not found"}), 404
    except Exception as e:
        logging.error(f"Error in redirect_to_long_url route: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True,port = 5000)
