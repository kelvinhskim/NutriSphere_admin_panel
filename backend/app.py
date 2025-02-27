from flask import Flask, json
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
    """Fetches all users from the database and displays them."""
    query = 'SELECT * FROM Users;'
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = json.dumps(cursor.fetchall())
    return results

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 55241)) 
    app.run(port=port, debug=True) 