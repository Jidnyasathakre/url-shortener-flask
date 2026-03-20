from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random
import validators
import os

app = Flask(__name__)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    short_code = db.Column(db.String(10), unique=True)
    clicks = db.Column(db.Integer, default=0)  

# Create Database
with app.app_context():
    db.create_all()

# Generate Short URL Code
def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    error = None

    if request.method == 'POST':
        original_url = request.form['url']

        # Validate URL
        if not validators.url(original_url):
            error = "Invalid URL"
        else:
            short_code = generate_short_code()

            new_url = URL(original_url=original_url, short_code=short_code)
            db.session.add(new_url)
            db.session.commit()

            short_url = request.host_url + short_code

    return render_template('index.html', short_url=short_url, error=error)


# Redirect Short URL
@app.route('/<short_code>')
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first_or_404()
    
    url.clicks += 1
    db.session.commit()

    return redirect(url.original_url)


# History Page
@app.route('/history')
def history():
    urls = URL.query.all()
    return render_template('history.html', urls=urls)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
