from flask import Flask, render_template, json, request, redirect, url_for
from flask_mysqldb import MySQL
import os
import database.db_connector as db

app = Flask(__name__)

# Connect to the database
db_connection = db.connect_to_database()

app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_kimh22'
app.config['MYSQL_PASSWORD'] = '0612' #last 4 of onid
app.config['MYSQL_DB'] = 'cs340_kimh22'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"


mysql = MySQL(app)


# Home Route
@app.route('/')
def home():
    """
    Renders the home page.
    """
    return render_template("index.html")

# READ - Display Users
@app.route('/users', methods=['GET'])
def users():
    """
    Fetches all users from the database and displays them.
    """
    query = "SELECT userID, username, email, dailyCalorieGoal FROM Users ORDER BY username;"
    cursor = db.execute_query(db_connection, query)
    users_data = cursor.fetchall()
    return render_template("users.html", users=users_data)

# CREATE - Add a User
@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Handles form submission to add a new user to the database.
    """
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    dailyCalorieGoal = request.form.get('dailyCalorieGoal', '')

    # Validate input
    if not username or not email or not dailyCalorieGoal.isdigit():
        print("Invalid input for adding user.")
        return redirect(url_for('users'))

    query = "INSERT INTO Users (username, email, dailyCalorieGoal) VALUES (%s, %s, %s);"
    db.execute_query(db_connection, query, (username, email, int(dailyCalorieGoal)))
    
    return redirect(url_for('users'))

# UPDATE - Modify a User
@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    """
    Updates a user's email or calorie goal in the database.
    """
    email = request.form.get('email', '').strip()
    dailyCalorieGoal = request.form.get('dailyCalorieGoal', '')

    if not email or not dailyCalorieGoal.isdigit():
        print("Invalid input for updating user.")
        return redirect(url_for('users'))

    query = "UPDATE Users SET email = %s, dailyCalorieGoal = %s WHERE userID = %s;"
    db.execute_query(db_connection, query, (email, int(dailyCalorieGoal), user_id))
    
    return redirect(url_for('users'))

# DELETE - Remove a User
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Deletes a user from the database.
    """
    query = "DELETE FROM Users WHERE userID = %s;"
    db.execute_query(db_connection, query, (user_id,))
    
    return redirect(url_for('users'))

# Additional Routes for Missing Pages
@app.route('/daily-trackers')
def daily_trackers():
    return render_template("daily-trackers.html")

@app.route('/food-entries')
def food_entries():
    return render_template("food-entries.html")

@app.route('/food-items')
def food_items():
    return render_template("food-items.html")


# READ - Display Exercises
@app.route('/exercises', methods=['GET'])
def exercises():
    """
    Fetches all exercises from the database and displays them.
    """
    query = "SELECT exerciseID, name, exerciseMinutes, caloriesBurned FROM Exercises ORDER BY name;"
    cursor = db.execute_query(db_connection, query)
    exercises_data = cursor.fetchall()
    return render_template("exercises.html", exercises=exercises_data)

# CREATE - Add an Exercise
@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    """
    Adds a new exercise to the database.
    """
    name = request.form.get('name', '').strip()
    exercise_minutes = request.form.get('exerciseMinutes', '')
    calories_burned = request.form.get('caloriesBurned', '')

    if not name or not exercise_minutes.isdigit() or not calories_burned.isdigit():
        print("Invalid input for adding exercise.")
        return redirect(url_for('exercises'))

    query = "INSERT INTO Exercises (name, exerciseMinutes, caloriesBurned) VALUES (%s, %s, %s);"
    db.execute_query(db_connection, query, (name, int(exercise_minutes), int(calories_burned)))

    return redirect(url_for('exercises'))

# UPDATE - Modify an Exercise
@app.route('/update_exercise/<int:exercise_id>', methods=['POST'])
def update_exercise(exercise_id):
    """
    Updates an exercise in the database.
    """
    name = request.form.get('name', '').strip()
    exerciseMinutes = request.form.get('exerciseMinutes', '')
    caloriesBurned = request.form.get('caloriesBurned', '')

    if not name or not exerciseMinutes.isdigit() or not caloriesBurned.isdigit():
        print("Invalid input for updating exercise.")
        return redirect(url_for('exercises'))

    query = "UPDATE Exercises SET name = %s, exerciseMinutes = %s, caloriesBurned = %s WHERE exerciseID = %s;"
    db.execute_query(db_connection, query, (name, int(exerciseMinutes), int(caloriesBurned), exercise_id))

    return redirect(url_for('exercises'))


# DELETE - Remove an Exercise
@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    """
    Deletes an exercise from the database.
    """
    query = "DELETE FROM Exercises WHERE exerciseID = %s;"
    db.execute_query(db_connection, query, (exercise_id,))

    return redirect(url_for('exercises'))  


# Start Application
if __name__ == "__main__":
    """
    Runs the Flask application.
    """
    app.run(host="0.0.0.0", port=65216, debug=True)