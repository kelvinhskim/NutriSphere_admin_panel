from flask import Flask
import os
import database.db_connector as db
from flask_cors import CORS

# Configuration
app = Flask(__name__)
db_connection = db.connect_to_database()
cors = CORS(app, origins='*')

# Routes 
@app.route('/')
def root():
    return "Hello World!!"

@app.get('/api/users')
def users():
    return "TA-DA! This is the users route"

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 55241)) 
    app.run(port=port, debug=True) 