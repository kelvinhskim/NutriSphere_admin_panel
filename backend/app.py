from flask import Flask, json, request, redirect, jsonify
import os
import database.db_connector as db
from flask_mysqldb import MySQL
from flask_cors import CORS

# Configuration
app = Flask(__name__)
db_connection = db.connect_to_database()
cors = CORS(app, origins='*')

# Routes 
@app.route('/')
def root():
    return "Hello World!!"

@app.route('/api/users', methods=['POST', 'GET', 'DELETE'])
def users():
    print('REQ METHOD', request.method)
    # Insert a new user into the Users entity
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')
        dailyCalorieGoal = request.json.get('dailyCalorieGoal')
        print('POST USER', username, email, dailyCalorieGoal)
        query = 'INSERT INTO Users (username, email, dailyCalorieGoal) VALUES (%s, %s, %s);'
        # cur = mysql.connection.cursor()
        # cur.execute(query, (username, email, dailyCalorieGoal))
        db.execute_query(db_connection=db_connection, query=query, query_params=(username, email, dailyCalorieGoal))
        db_connection.commit()
        return redirect('/api/users')

    # Grabs all users data to send to frontend browse users table
    if request.method == "GET":
        query = 'SELECT userID, username, email, dailyCalorieGoal FROM Users ORDER BY username;'
        cursor = db.execute_query(db_connection=db_connection, query=query)
        results = json.dumps(cursor.fetchall())
        return results
    
@app.route('/api/delete_user/<int:userID>', methods=['DELETE'])
def delete_user(userID):
    print('DELETE USER REQ', userID)
    query = 'DELETE FROM Users WHERE userID = %s;'
    db.execute_query(db_connection=db_connection, query=query, query_params=(userID,))
    db_connection.commit()
    return jsonify({'message': f'Deleted user: {userID}'}) 

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 55241)) 
    app.run(port=port, debug=True) 