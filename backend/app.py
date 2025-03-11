# Citation for the following function:
# Date: 02/27/2025  (Update to the date you copied/used it)
# Copied from /OR/ Adapted from /OR/ Based on:
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app


from flask import Flask, render_template, request, json, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# database connection
# Template:
# app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
# app.config["MYSQL_USER"] = "cs340_OSUusername"
# app.config["MYSQL_PASSWORD"] = "XXXX" | last 4 digits of OSU id
# app.config["MYSQL_DB"] = "cs340_OSUusername"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# database connection info
app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_kimh22'
app.config['MYSQL_PASSWORD'] = '0612' #last 4 of onid
app.config['MYSQL_DB'] = 'cs340_kimh22'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app) # Initialize MySQL with Flask app

# --------------------------------------------------
# Home Route
@app.route('/')
def home():
    """
    Renders the home page.
    """
    return render_template("index.html")


# --------------------------------------------------
# Read - Display Users (GET Request)
@app.route('/users', methods=['GET'])
def users():
    """
    Fetches all users from the database and displays them.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Execute the SQL query to retrieve all users
        query = "SELECT userID, username, email, dailyCalorieGoal FROM Users ORDER BY username;"
        cursor.execute(query)
        
        # Fetch all results from the query
        users_data = cursor.fetchall()
        
        recommended_users = [
            {'id': 1, 'username': 'Tyler', 'email': 'tyler@oregonstate.edu', 'dailyCalorieGoal': 2400},
            {'id': 2, 'username': 'Jane', 'email': 'jane@oregonstate.edu', 'dailyCalorieGoal': 2000},
            {'id': 3, 'username': 'Alex', 'email': 'alex@oregonstate.edu', 'dailyCalorieGoal': 2200}
        ]

        # Return the users data to the 'users.html' template
        return render_template("users.html", users=users_data, recommended_users=recommended_users)
    
    except Exception as e:
        print("❌ Error fetching users:", e)
        return redirect(url_for('home'))  # Redirect to home in case of error


# --------------------------------------------------
# Create - Add a User (POST Request)
@app.route("/add_user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    email = request.form.get("email")
    dailyCalorieGoal = request.form.get("dailyCalorieGoal")
    
    # Check if inputs are valid
    if not username or not email or not dailyCalorieGoal:
        return "Error: All fields are required", 400
    
    # Ensure dailyCalorieGoal is a valid number (isdigit check after type conversion)
    if not dailyCalorieGoal.isdigit():
        return "Error: Daily Calorie Goal must be a number", 400
    
    # Now, you can safely cast dailyCalorieGoal to an integer
    dailyCalorieGoal = int(dailyCalorieGoal)

    try:
        # Get a cursor from the database connection
        cursor = mysql.connection.cursor()

        # Execute the SQL query to insert the new user
        query = "INSERT INTO Users (username, email, dailyCalorieGoal) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, dailyCalorieGoal))

        # Commit the transaction to the database
        mysql.connection.commit()
        # Close the cursor after the operation
        cursor.close()

        # Optionally, print confirmation for debugging
        print(f"✅ User {username} added successfully!")
        return redirect(url_for('users'))

    except Exception as e:
        # If there's an error, print it and return an error message
        print(f"❌ Error adding user: {e}")
        return redirect(url_for('users'))


# --------------------------------------------------
# Update - Modify a User (POST Request)
@app.route("/update_user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    email = request.form.get("email", "").strip()
    dailyCalorieGoal = request.form.get("dailyCalorieGoal", "").strip()

    if not email or not dailyCalorieGoal.isdigit():
        return "Error: Invalid input", 400

    dailyCalorieGoal = int(dailyCalorieGoal)

    cursor = mysql.connection.cursor()
    query = "UPDATE Users SET email=%s, dailyCalorieGoal=%s WHERE userID=%s"
    cursor.execute(query, (email, dailyCalorieGoal, user_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('users'))

    
# --------------------------------------------------
# Delete - Remove a User (POST Request)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Deletes a user from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Construct the SQL DELETE query
        query = "DELETE FROM Users WHERE userID = %s;"
        
        # Execute the query with the user ID to be deleted
        cursor.execute(query, (user_id,))
        
        # Commit the transaction to the database
        mysql.connection.commit()
        cursor.close()
        
        print(f"✅ User {user_id} deleted successfully!")
        return jsonify({"message": "User deleted", "user_id": user_id}), 200
    
    except Exception as e:
        print(f"❌ Error deleting user:", e)
        return jsonify({"error": "Internal Server Error"}), 500



# --------------------------------------------------
# Read - Retrieves DailyTrackers data (GET Request)
@app.route('/daily-trackers', methods=["GET"])
def daily_trackers():
    try:
        # Main query with JOIN to fetch Username and Exercise Name
        query = (
            "SELECT "
            "dt.dailyTrackerID AS `Daily Tracker ID`, "
            "u.username AS `Username`, "
            "dt.date AS `Date`, "
            "dt.calorieGoal AS `Calorie Goal`, "
            "dt.caloriesConsumed AS `Calories Consumed`, "
            "COALESCE(e.caloriesBurned, 0) AS `Calories Burned`, "
            "dt.caloriesRemaining AS `Calories Remaining`, "
            "COALESCE(e.name, 'Null') AS `Exercise Logged` "
            "FROM DailyTrackers dt "
            "LEFT JOIN Users u ON dt.userID = u.userID "
            "LEFT JOIN Exercises e ON dt.exerciseID = e.exerciseID "
            "ORDER BY dt.date DESC;"
        )
        cur = mysql.connection.cursor()
        cur.execute(query)
        dailytrackers_data = cur.fetchall()

        # Query for Users dropdown
        query2 = "SELECT userID, username, dailyCalorieGoal FROM Users;"
        cur.execute(query2)
        users_data = cur.fetchall()

        # Query for Exercises dropdown
        query3 = "SELECT exerciseID, name, caloriesBurned FROM Exercises;"
        cur.execute(query3)
        exercises_data = cur.fetchall()

        # Query for DailyTrackers dropdown (for updating)
        query4 = (
            "SELECT "
            "dt.dailyTrackerID, u.userID, u.username, dt.date, dt.calorieGoal, e.exerciseID, e.name AS `exerciseName` "
            "FROM DailyTrackers AS dt "
            "LEFT JOIN Users AS u ON dt.userID = u.userID "
            "LEFT JOIN Exercises as e ON dt.exerciseID = e.exerciseID;"
        )
        cur.execute(query4)
        dailytrackers_dropdown_data = cur.fetchall()

        cur.close()
        
        # Return page with data
        return render_template(
            "daily-trackers.html",
            daily_trackers=dailytrackers_data,
            users=users_data,
            exercises=exercises_data,
            daily_trackers_dropdown=dailytrackers_dropdown_data
        )
    
    except Exception as e:
        print("❌ Error fetching daily trackers data:", e)
        return "An error occurred while fetching data", 500


# --------------------------------------------------
# Create - Inserts a new daily tracker into the DailyTrackers table (POST Request)
@app.route('/add-tracker', methods=["POST"])
def add_tracker():
    date = request.form["date"]
    userID = request.form["userID"]
    # username = request.form["username"]
    calorieGoal = request.form["calorieGoal"]
    exerciseID = request.form["exerciseID"]
    try:
        # query if no exercise is input in the exercise field
        if exerciseID == "NULL":
            query = "INSERT INTO DailyTrackers (date, calorieGoal, userID) VALUES (%s, %s, %s)"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorieGoal, userID))
            mysql.connection.commit()
            cur.close()   
        else:
            # query to insert a new daily tracker into DailyTrackers
            query = "INSERT INTO DailyTrackers (date, calorieGoal, userID, exerciseID) VALUES (%s, %s, %s, %s)"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorieGoal, userID, exerciseID))
            mysql.connection.commit()
            cur.close()   
        
        print(f"✅  DailyTracker added successfully!")
        return redirect("/daily-trackers")
    except Exception as e:
        print("❌ Error adding new daily tracker:", e)    
        return "An error occurred while adding a tracker", 500


# --------------------------------------------------
# Update - Updates a selected daily tracker (POST Request)
@app.route('/update-tracker', methods=["POST"])
def update_tracker():
    # print("REQUEST FORM:", request.form.get("Update_Daily_Tracker"), request.form)
    trackerID = request.form["trackerID"]
    date = request.form["date"]
    calorieGoal = request.form["calorie-goal"]
    userID = request.form["userID"]
    exerciseID = request.form["exerciseID"]
    # print("UPDATE DATA", trackerID, date, calorieGoal, userID, exerciseID)
    try:
        # query if no exercise is input in the exercise field
        if exerciseID == "NULL":
            query = "UPDATE DailyTrackers SET date = %s, calorieGoal = %s, userID = %s, exerciseID = %s WHERE dailyTrackerID = %s;"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorieGoal, userID, "NUll", trackerID))
            mysql.connection.commit()
            cur.close()   
        else:
            # query to update daily tracker
            query = "UPDATE DailyTrackers SET date = %s, calorieGoal = %s, userID = %s, exerciseID = %s WHERE dailyTrackerID = %s;"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorieGoal, userID, exerciseID, trackerID))
            mysql.connection.commit()
            cur.close()   
        print(f"✅  DailyTracker {trackerID} updated successfully!")
        return redirect("/daily-trackers")
    except Exception as e: 
        print("❌ Error updating tracker:", e)   
        return "An error occurred while adding a tracker", 500


# --------------------------------------------------
# Delete - Deletes a selected daily tracker ( Request)
@app.route('/delete-tracker', methods=["POST"])
def delete_tracker():
    tracker_id = request.form['trackerID']  # Daily Tracker ID to delete
    try:
        if tracker_id:
            query = "DELETE FROM DailyTracker WHERE dailyTrackerID = ?"
            cursor.execute(query, (tracker_id,))
            db.commit()
            flash("Daily Tracker deleted successfully!")
        else:
            flash("Error: Tracker ID not found!")

    except Exception as e:
        print("❌ Error deleting tracker:", e)
        flash("An error occurred while deleting the tracker.")
    return redirect(url_for('daily_trackers'))


# --------------------------------------------------
@app.route('/food-entries')
def food_entries():
    return render_template("food-entries.html")


# --------------------------------------------------
# READ - Display Food Items
@app.route('/food-items', methods=['GET'])
def food_items():
    """
    Fetches all food items from the database and displays them.
    """
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT foodItemID, name, brand, servingSize, calories, protein, fat, carbohydrates
            FROM FoodItems
            ORDER BY name;
        """
        cursor.execute(query)
        food_items_data = cursor.fetchall()

        recommended_foods = [
            {'id': 1, 'name': 'Oatmeal', 'brand': 'Quaker', 'servingSize': '1 cup', 'calories': 153, 'protein': 5, 'fat': 3, 'carbohydrates': 27},
            {'id': 2, 'name': 'Coffee', 'brand': 'Starbucks', 'servingSize': '1 cup (grande)', 'calories': 15, 'protein': 1, 'fat': 0, 'carbohydrates': 2},
            {'id': 3, 'name': 'Salad', 'brand': 'NULL', 'servingSize': '1 bowl', 'calories': 250, 'protein': 7, 'fat': 10, 'carbohydrates': 30},
            {'id': 4, 'name': 'Chicken', 'brand': "Trader Joe\'s", 'servingSize': '113g', 'calories': 150, 'protein': 27, 'fat': 4, 'carbohydrates': 0},
            {'id': 5, 'name': 'Brown Rice', 'brand': 'Nishiki', 'servingSize': '210g', 'calories': 340, 'protein': 7, 'fat': 2, 'carbohydrates': 7},
            {'id': 6, 'name': 'Big Mac', 'brand': "McDonald\'s", 'servingSize': '1 burger', 'calories': 580, 'protein': 25, 'fat': 34, 'carbohydrates': 45},
        ]  

        return render_template("food-items.html", food_items=food_items_data, recommended_foods=recommended_foods)

    except Exception as e:
        print("❌ Error fetching food items:", e)
        return redirect(url_for('home'))


# --------------------------------------------------
# CREATE - Add a Food Item
@app.route('/add_food_item', methods=['POST'])
def add_food_item():
    """
    Adds a new food item to the database.
    """
    name = request.form.get('name', '').strip()
    brand = request.form.get('brand', '').strip()
    serving_size = request.form.get('servingSize', '').strip()
    calories = request.form.get('calories', '')
    protein = request.form.get('protein', '')
    fat = request.form.get('fat', '')
    carbohydrates = request.form.get('carbohydrates', '')

    # Validate numeric inputs
    try:
        calories = int(calories)
        protein = int(protein)
        fat = int(fat)
        carbohydrates = int(carbohydrates)
    except ValueError:
        print("❌ Invalid input: Non-numeric value in numeric fields.")
        return redirect(url_for('food_items'))

    try:
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO FoodItems (name, brand, servingSize, calories, protein, fat, carbohydrates)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (name, brand, serving_size, calories, protein, fat, carbohydrates))
        mysql.connection.commit()
        print(f"✅ Food item '{name}' added successfully!")
    except Exception as e:
        print("❌ Error adding food item:", e)

    return redirect(url_for('food_items'))


# --------------------------------------------------
# UPDATE - Modify a Food Item
@app.route('/update_food_item/<int:food_item_id>', methods=['POST'])
def update_food_item(food_item_id):
    """
    Updates an existing food item in the database.
    """
    name = request.form.get('name', '').strip()
    brand = request.form.get('brand', '').strip()
    serving_size = request.form.get('servingSize', '').strip()
    calories = request.form.get('calories', '')
    protein = request.form.get('protein', '')
    fat = request.form.get('fat', '')
    carbohydrates = request.form.get('carbohydrates', '')

    # Validate numeric inputs using try-except
    try:
        calories = int(calories)
        protein = int(protein)
        fat = int(fat)
        carbohydrates = int(carbohydrates)
    except ValueError:
        print("❌ Invalid input: Non-numeric value in numeric fields.")
        return redirect(url_for('food_items'))

    try:
        cursor = mysql.connection.cursor()
        query = """
            UPDATE FoodItems
            SET name = %s, brand = %s, servingSize = %s, calories = %s, protein = %s, fat = %s, carbohydrates = %s
            WHERE foodItemID = %s;
        """
        cursor.execute(query, (name, brand, serving_size, calories, protein, fat, carbohydrates, food_item_id))
        mysql.connection.commit()
        print(f"✅ Food item '{name}' (ID: {food_item_id}) updated successfully!")
    except Exception as e:
        print(f"❌ Error updating food item (ID: {food_item_id}):", e)

    return redirect(url_for('food_items'))


#--------------------------------------------------
# DELETE - Remove a Food Item
@app.route('/delete_food_item/<int:food_item_id>', methods=['POST'])
def delete_food_item(food_item_id):
    """
    Deletes a food item from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM FoodItems WHERE foodItemID = %s;"
        cursor.execute(query, (food_item_id,))
        mysql.connection.commit()
        print(f"✅ Food item ID {food_item_id} deleted successfully!")
    except Exception as e:
        print(f"❌ Error deleting food item (ID: {food_item_id}):", e)

    return redirect(url_for('food_items'))


# --------------------------------------------------
# READ - Display Exercises
@app.route('/exercises', methods=['GET'])
def exercises():
    """
    Fetches all exercises from the database and displays them.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT exerciseID, name, exerciseMinutes, caloriesBurned FROM Exercises ORDER BY name;"
        cursor.execute(query)
        exercises_data = cursor.fetchall()

        # Recommended Exercises (Hardcoded)
        recommended_exercises = [
            {'id': 1, 'name': 'Elliptical', 'exerciseMinutes': 30, 'caloriesBurned': 250},
            {'id': 2, 'name': 'Hiking', 'exerciseMinutes': 120, 'caloriesBurned': 600},
            {'id': 3, 'name': 'Swimming', 'exerciseMinutes': 30, 'caloriesBurned': 300},
            {'id': 4, 'name': 'Pickleball', 'exerciseMinutes': 60, 'caloriesBurned': 400},
            {'id': 5, 'name': 'Weight Lifting', 'exerciseMinutes': 60, 'caloriesBurned': 150}
        ]

        return render_template("exercises.html", exercises=exercises_data, recommended_exercises=recommended_exercises)
    except Exception as e:
        print("❌ Error fetching exercises:", e)
        return redirect(url_for('home'))


# --------------------------------------------------
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

    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Exercises (name, exerciseMinutes, caloriesBurned) VALUES (%s, %s, %s);"
        cursor.execute(query, (name, int(exercise_minutes), int(calories_burned)))
        mysql.connection.commit()
        print(f"✅ Exercise '{name}' added successfully!")
    except Exception as e:
        print("❌ Error adding exercise:", e)

    return redirect(url_for('exercises'))

# --------------------------------------------------
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

    try:
        cursor = mysql.connection.cursor()
        query = "UPDATE Exercises SET name = %s, exerciseMinutes = %s, caloriesBurned = %s WHERE exerciseID = %s;"
        cursor.execute(query, (name, int(exerciseMinutes), int(caloriesBurned), exercise_id))
        mysql.connection.commit()
        print(f"✅ Exercise '{name}' updated successfully!")
    except Exception as e:
        print("❌ Error updating exercise:", e)

    return redirect(url_for('exercises'))

# --------------------------------------------------
# DELETE - Remove an Exercise
@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    """
    Deletes an exercise from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Exercises WHERE exerciseID = %s;"
        cursor.execute(query, (exercise_id,))
        mysql.connection.commit()
        print(f"✅ Exercise ID {exercise_id} deleted successfully!")
    except Exception as e:
        print("❌ Error deleting exercise:", e)

    return redirect(url_for('exercises'))

# --------------------------------------------------
# Start Application
if __name__ == "__main__":
    """
    Runs the Flask application.
    """
    app.run(host="0.0.0.0", port=65216, debug=True)