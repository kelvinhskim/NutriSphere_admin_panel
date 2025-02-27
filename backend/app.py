from flask import Flask
import os
import database.db_connector as db

# Configuration
app = Flask(__name__)
db_connection = db.connect_to_database()

# Routes 
@app.route('/')
def root():
    return "Hello Bloop!!"

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 55241)) 
    app.run(port=port, debug=True) 