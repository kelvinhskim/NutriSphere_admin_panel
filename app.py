from flask import Flask, render_template, json, jsonify
from flask_cors import CORS
import os
import database.db_connector as db

# Configuration
app = Flask(__name__)
cors = CORS(app, origins='*')
db_connection = db.connect_to_database()


# Routes
@app.route('/')
def root():
    return "Hello, World!"


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 55241))
    app.run(port=port, debug=True)
