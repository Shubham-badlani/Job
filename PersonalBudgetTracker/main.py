import os
import logging
from app import app
from flask import render_template_string

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Add a test route to check if the server is working
@app.route('/test')
def test():
    return render_template_string('<h1>AI Recruitment System Test Page</h1><p>If you can see this, the server is working correctly!</p>')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
