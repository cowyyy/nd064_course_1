import logging
import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connection_count = 0
def get_db_connection():
    global db_connection_count
    db_connection_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
posts_count = 0
def get_post(post_id):
    global posts_count
    posts_count += 1
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Error 404: Page not found!!')
      return render_template('404.html'), 404
    else:
      app.logger.info(f"Article {post['title']} retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f"New article created: {title}")

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({ 
            'result': 'OK - healthy'
        }),
        status=200,
        mimetype = 'application/json',
    )

    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({
            'posts_count': posts_count,
            'db_connection_count': db_connection_count
        }),
        status=200,
        mimetype = 'application/json',
    )

    return response

# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers = [stdout_handler, stderr_handler]
    format_output = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)

    app.run(host='0.0.0.0', port='3111')
