from flask import Flask, render_template, request, json, redirect, url_for, jsonify, flash
from flask_mysqldb import MySQL
import os
import subprocess

# Citation for the following function:
# Date: 02/27/2025
# Originality: Adapted
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app
# Description: Copied and adapted from the OSU CS340 Flask Starter App for database connections and routing.

# Citation for the following references:
# Date: 03/14/2025
# Originality: Referenced
# Source URL: https://www.geeksforgeeks.org/sql-ddl-dml-tcl-dcl/
# Description: Used as a reference for understanding SQL command classifications (DDL, DML, TCL, DCL).

# Date: 03/14/2025
# Originality: Referenced
# Source URL: https://www.w3schools.com/sql/sql_syntax.asp
# Description: Referenced for SQL syntax rules and query structure.

# Date: 03/14/2025
# Originality: Referenced
# Source URL: https://www.geeksforgeeks.org/how-to-serve-static-files-in-flask/
# Description: Used as a guide for serving static files in Flask applications.

# Date: 03/14/2025
# Originality: Referenced
# Source URL: https://flask.palletsprojects.com/en/stable/patterns/javascript/
# Description: Referenced for integrating JavaScript patterns within Flask applications.

# Date: 03/14/2025
# Originality: Referenced
# Source URL: https://www.geeksforgeeks.org/flask-app-routing/
# Description: Used as a reference for understanding Flask routing mechanisms.

app = Flask(__name__)
app.secret_key = "secret key"

# Database connection info with credentials sanitized.
# app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
# app.config["MYSQL_USER"] = "cs340_OSUusername"
# app.config["MYSQL_PASSWORD"] = "XXXX"
# app.config["MYSQL_DB"] = "cs340_OSUusername"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# database connection info
app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_xxxx'
app.config['MYSQL_PASSWORD'] = 'XXXX' #last 4 of onid
app.config['MYSQL_DB'] = 'cs340_xxxx'
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


# --------------USERS CRUD-----------------------------

# --------------Read (Display Users)--------------------
@app.route("/users", methods=["GET"])
def users():
    """
    Display all users in a table format.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Users"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()

        return render_template("users.html", users=users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return "Internal Server Error", 500


# --------------Create Users---------------------------
@app.route("/create_user", methods=["POST"])
def create_user():
    """
    Create a new user in the database.
    """
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    dailyCalorieGoal = request.form.get("dailyCalorieGoal", "").strip()

    if not username or not email or not dailyCalorieGoal.isdigit():
        flash("All fields are required and dailyCalorieGoal must be a number.")
        return redirect(url_for('users'))

    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Users (username, email, dailyCalorieGoal) VALUES (%s, %s, %s);"
        cursor.execute(query, (username, email, int(dailyCalorieGoal)))
        mysql.connection.commit()
        cursor.close()

        flash(f"User '{username}' added successfully!")
        return redirect(url_for('users'))

    except Exception as e:
        print(f"Error creating user: {e}")
        flash("Failed to add user.")
        return redirect(url_for('users'))


# --------------Update Users---------------------------
@app.route("/update_user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    """
    Update an existing user in the database.
    """
    email = request.form.get("email", "").strip()
    dailyCalorieGoal = request.form.get("dailyCalorieGoal", "").strip()

    if not email or not dailyCalorieGoal.isdigit():
        flash("Invalid input. Ensure fields are not empty and dailyCalorieGoal is a number.")
        return redirect(url_for('users'))

    try:
        cursor = mysql.connection.cursor()
        query = "UPDATE Users SET email=%s, dailyCalorieGoal=%s WHERE userID=%s;"
        cursor.execute(query, (email, int(dailyCalorieGoal), user_id))
        mysql.connection.commit()
        cursor.close()

        flash(f"User ID {user_id} updated successfully!")
        return redirect(url_for('users'))

    except Exception as e:
        print(f"Error updating user: {e}")
        flash("Failed to update user.")
        return redirect(url_for('users'))


# ---------- Delete (Remove User) ----------
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Delete a user from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Users WHERE userID = %s;"
        cursor.execute(query, (user_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "User deleted", "user_id": user_id}), 200
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



# --------------Daily Trackers CRUD-----------------------------

# --------------------------------------------------
# Read - Retrieves DailyTrackers data (GET Request)
@app.route('/daily-trackers', methods=["GET"])
def daily_trackers():
    try:
        # Main query with JOIN to fetch Username and Exercise Name and calculate calories
        query = """
            SELECT 
                dt.dailyTrackerID AS `Daily Tracker ID`, 
                u.username AS `Username`, 
                dt.date AS `Date`, 
                dt.calorieGoal AS `Calorie Goal`, 
                (SELECT IFNULL(SUM(fi.calories), 0)
                    FROM FoodEntries fe
                    LEFT JOIN FoodItems fi ON fe.foodItemID = fi.foodItemID
                    WHERE fe.dailyTrackerID = dt.dailyTrackerID) AS `Calories Consumed`,
                IFNULL(e.caloriesBurned, 0) AS `Calories Burned`, 
                (dt.calorieGoal - (SELECT IFNULL(SUM(fi.calories), 0)
                    FROM FoodEntries fe
                    LEFT JOIN FoodItems fi ON fe.foodItemID = fi.foodItemID
                    WHERE fe.dailyTrackerID = dt.dailyTrackerID) 
                    + IFNULL(e.caloriesBurned, 0)) AS `Calories Remaining`, 
                IFNULL(e.name, 'No Exercise Logged') AS `Exercise Logged` 
            FROM DailyTrackers dt 
            LEFT JOIN Users u ON dt.userID = u.userID 
            LEFT JOIN Exercises e ON dt.exerciseID = e.exerciseID 
            ORDER BY dt.date ASC, u.username ASC;
        """
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
        query4 = """
            SELECT
            dt.dailyTrackerID, u.userID, u.username, dt.date, dt.calorieGoal, e.exerciseID, e.name AS `exerciseName`
            FROM DailyTrackers AS dt
            LEFT JOIN Users AS u ON dt.userID = u.userID
            LEFT JOIN Exercises as e ON dt.exerciseID = e.exerciseID;
        """
        cur.execute(query4)
        dailytrackers_dropdown_data = cur.fetchall()
        # print(dailytrackers_dropdown_data)

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
@app.route('/daily-trackers', methods=["POST"])
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
        print(f"DailyTracker added successfully!")
        return redirect("/daily-trackers")
    except Exception as e:
        print("Error adding new daily tracker:", e)    
        return "An error occurred while adding a tracker", 500


# --------------------------------------------------
# Update - Updates a selected daily tracker (PUT Request)
@app.route('/daily-trackers/<int:tracker_id>', methods=["PUT"])
def update_tracker(tracker_id):
    data = request.get_json()
    date = data["date"]
    calorie_goal = data["calorieGoal"]
    user_id = data["userID"]
    exercise_id = data["exerciseID"]
    print("exercise", exercise_id, type(exercise_id))
    try:
        # query if no exercise is input in the exercise field
        if exercise_id == "NULL":
            query = "UPDATE DailyTrackers SET date = %s, calorieGoal = %s, userID = %s, exerciseID = %s WHERE dailyTrackerID = %s;"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorie_goal, user_id, None, tracker_id))
            mysql.connection.commit()
            cur.close()   
        else:
            # query to update daily tracker
            query = "UPDATE DailyTrackers SET date = %s, calorieGoal = %s, userID = %s, exerciseID = %s WHERE dailyTrackerID = %s;"
            cur = mysql.connection.cursor() 
            cur.execute(query, (date, calorie_goal, user_id, exercise_id, tracker_id))
            mysql.connection.commit()
            cur.close()   
        print(f"DailyTracker {tracker_id} updated successfully!")
        return jsonify({
            "message": f"DailyTracker {tracker_id} updated successfully.",
            "redirect_url": "/daily-trackers"
            }), 200
    except Exception as e: 
        print("Error updating tracker {tracker_id}:", e)   
        return "An error occurred while updating tracker {tracker_id}", 500


# --------------------------------------------------
# Delete - Deletes a selected daily tracker (DELETE Request)
@app.route('/daily-trackers/<int:tracker_id>', methods=["DELETE"])
def delete_tracker(tracker_id):
    try:
        query = "DELETE FROM DailyTrackers WHERE dailyTrackerID = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (tracker_id,))
        mysql.connection.commit()
        print(f"DailyTracker {tracker_id} deleted successfully!")
        return jsonify({
            "message": f"DailyTracker {tracker_id} deleted successfully.",
            "redirect_url": "/daily-trackers"
            }), 200
    except Exception as e:
        print("Error deleting DailyTracker {tracker_id}:", e)
        return "An error occurred while deleting tracker {tracker_id}", 500
    

# --------------Foor Entries CRUD-------------------

# --------------------------------------------------
# Read - Retrieves FoodEntries data (GET Request)
@app.route('/food-entries', methods=["GET"])
def food_entries():
    try:
        # Query to retrieve all food entries which are associated with users' daily trackers
        query = """
            SELECT 
                fe.foodEntryID AS `Food Entry ID`, 
                fe.mealCategory AS `Meal Category`,
                CASE
                    WHEN fi.brand IS NULL THEN fi.name
                    ELSE CONCAT(fi.name, ', ', IFNULL(fi.brand, '')) 
                    END AS `Food`, 
                fi.calories AS `Calories`, 
                CONCAT(dt.dailyTrackerID, ': ', u.username, ', ', dt.date) AS `Daily Tracker` 
            FROM FoodEntries AS fe 
            JOIN DailyTrackers AS dt ON fe.dailyTrackerID = dt.dailyTrackerID 
            JOIN Users AS u ON dt.userID = u.userID 
            JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID 
            ORDER BY dt.date ASC, u.username ASC, 
                CASE 
                    WHEN fe.mealCategory = 'Breakfast' then 1 
                    WHEN fe.mealCategory = 'Lunch' then 2 
                    WHEN fe.mealCategory = 'Dinner' then 3 
                    WHEN fe.mealCategory = 'Snacks' then 4 
                END ASC;
            """
        cur = mysql.connection.cursor()
        cur.execute(query)
        food_entries_data = cur.fetchall()
        # print(food_entries_data)

        # Query for Users dropdown
        query2 = "SELECT userID, username, dailyCalorieGoal FROM Users ORDER BY username;"
        cur.execute(query2)
        users_data = cur.fetchall()

        # Query for Food Item dropdown
        query3 = "SELECT foodItemID, name, brand FROM FoodItems;"
        cur.execute(query3)
        food_item_dropdown_data = cur.fetchall()
        # print(food_item_dropdown_data)

        # Query for Food Entry Update 
        query4 = """
            SELECT fe.foodEntryID, fe.mealCategory, fi.foodItemID, fi.name, dt.dailyTrackerID, dt.date, u.username
                FROM FoodEntries AS fe
                LEFT JOIN DailyTrackers AS dt ON fe.dailyTrackerID = dt.dailyTrackerID
                JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID
                JOIN Users AS u ON dt.userID = u.userID;
            """
        cur.execute(query4)
        food_entry_update_data = cur.fetchall()
        # print("food entry update data", food_entry_update_data)

        # Query for Daily Trackers dropdown 
        query5 = """
            SELECT dt.dailyTrackerID, u.username, dt.date 
                FROM DailyTrackers dt
                JOIN Users u ON dt.userID = u.userID
                ORDER BY dt.date DESC, u.username DESC;
            """
        cur.execute(query5)
        daily_tracker_dropdown_data = cur.fetchall()

        cur.close()
        return render_template(
            "food-entries.html", 
            food_entries=food_entries_data,
            users=users_data,
            food_item_dropdown=food_item_dropdown_data,
            food_entry_update=food_entry_update_data,
            daily_tracker_dropdown=daily_tracker_dropdown_data
        )
    except Exception as e:
        print("Error fetching food entries data:", e)
        return "An error occurred while fetching food entries data", 500


# --------------------------------------------------
# CREATE - Inserts an entry into the Food Entries table (POST Request)
@app.route('/food-entries', methods=['POST'])
def add_food_entry():
    # print(request.form)
    user_id = request.form["userID"]
    date = request.form["date"]
    meal_category = request.form["mealCategory"]
    food_item_id = request.form["foodItemID"]
    try:
        query = "CALL add_food_entry(%s, %s, %s, %s);"
        cur = mysql.connection.cursor()
        cur.execute(query, (user_id, date, meal_category, food_item_id))
        mysql.connection.commit()
        cur.close()  
        print(f"FoodEntry added successfully!")
        return redirect("/food-entries")
    except Exception as e:
        print("Error adding food entries data:", e)
        return f"An error occurred while adding food entries data: {e}", 500
    

# --------------------------------------------------
# UPDATE - Updates a selected food entry in the Food Entries table (PUT Request)
@app.route('/food-entries/<int:food_entry_id>', methods=["PUT"])
def update_food_entry(food_entry_id):
    data = request.get_json()
    meal_category = data["mealCategory"]
    food_item_id = data["foodItemID"]
    daily_tracker_id = data["dailyTrackerID"]
    try:
        query = "UPDATE FoodEntries SET mealCategory = %s, foodItemID = %s, dailyTrackerID = %s WHERE foodEntryID = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (meal_category, food_item_id, daily_tracker_id, food_entry_id))
        mysql.connection.commit()
        cur.close()
        print(f"FoodEntry updated successfully!")
        return jsonify({
            "message": f"FoodEntry {food_entry_id} updated successfully.",
            "redirect_url": "/food-entries"
        }), 200
    except Exception as e:
        print("Error updating food entries data:", e)
        return "An error occurred while updating a food entry", 500


# --------------------------------------------------
# DELETE - Deletes a selected food entry in the Food Entries table (DELETE Request)
@app.route("/food-entries/<int:entry_id>", methods=["DELETE"])
def delete_food_entry(entry_id):
    try:
        query = "DELETE FROM FoodEntries WHERE foodEntryID = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (entry_id,))
        mysql.connection.commit()
        print(f"FoodEntry {entry_id} deleted successfully!")
        return jsonify({
            "message": f"FoodEntry {entry_id} deleted successfully.",
            "redirect_url": "/food-entries"
            }), 200
    except Exception as e:
        print("Error deleting FoodEntry {entry_id}:", e)
        return "An error occurred while deleting an entry", 500


# --------------Food Items CRUD-----------------------------

# ---------------------- Read (Display Food Items) ----------------------
@app.route("/food_items", methods=["GET"])
def food_items():
    """
    Display all food items.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM FoodItems"
        cursor.execute(query)
        food_items = cursor.fetchall()
        cursor.close()

        return render_template("food_items.html", food_items=food_items)
    except Exception as e:
        print(f"Error fetching food items: {e}")
        return "Internal Server Error", 500


# ---------------------- Create (Add New Food Item) ----------------------
@app.route("/add_food_item", methods=["POST"])
def add_food_item():
    """
    Add a new food item to the database.
    """
    name = request.form.get("name", "").strip()
    brand = request.form.get("brand", "").strip()
    servingSize = request.form.get("servingSize", "").strip()
    calories = request.form.get("calories", "").strip()
    protein = request.form.get("protein", "").strip()
    fat = request.form.get("fat", "").strip()
    carbohydrates = request.form.get("carbohydrates", "").strip()

    if not name or not calories.isdigit():
        flash("Name and calories are required. Calories must be a number.")
        return redirect(url_for('food_items'))

    try:
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO FoodItems (name, brand, servingSize, calories, protein, fat, carbohydrates)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            name, brand or None, servingSize or None, int(calories),
            int(protein) if protein.isdigit() else 0,
            int(fat) if fat.isdigit() else 0,
            int(carbohydrates) if carbohydrates.isdigit() else 0
        ))
        mysql.connection.commit()
        cursor.close()

        flash(f"Food item '{name}' added successfully!")
        return redirect(url_for('food_items'))

    except Exception as e:
        print(f"Error adding food item: {e}")
        flash("Failed to add food item.")
        return redirect(url_for('food_items'))


# ---------------------- Update Food Item ----------------------
@app.route("/update_food_item/<int:food_item_id>", methods=["POST"])
def update_food_item(food_item_id):
    name = request.form.get("name", "").strip()
    brand = request.form.get("brand", "").strip()
    servingSize = request.form.get("servingSize", "").strip()
    calories = request.form.get("calories", "").strip()
    protein = request.form.get("protein", "").strip()
    fat = request.form.get("fat", "").strip()
    carbohydrates = request.form.get("carbohydrates", "").strip()

    print("=== UPDATE RECEIVED ===")
    print(name, brand, servingSize, calories, protein, fat, carbohydrates)

    try:
        cursor = mysql.connection.cursor()
        query = """
            UPDATE FoodItems
            SET name=%s, brand=%s, servingSize=%s, calories=%s, protein=%s, fat=%s, carbohydrates=%s
            WHERE foodItemID=%s;
        """
        cursor.execute(query, (name, brand or None, servingSize or None, int(calories),
                               int(protein) if protein else 0, int(fat) if fat else 0, int(carbohydrates) if carbohydrates else 0,
                               food_item_id))
        mysql.connection.commit()
        cursor.close()
        print("UPDATE SUCCESS")
        return redirect(url_for('food_items'))
    except Exception as e:
        print(f"Error updating food item: {e}")
        return redirect(url_for('food_items'))


# ---------------------- Delete (Remove Food Item) ----------------------
@app.route("/delete_food_item/<int:food_item_id>", methods=["POST"])
def delete_food_item(food_item_id):
    """
    Delete a food item from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM FoodItems WHERE foodItemID = %s;"
        cursor.execute(query, (food_item_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Food item deleted", "food_item_id": food_item_id}), 200
    except Exception as e:
        print(f"Error deleting food item: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


# --------------EXERCISES CRUD-----------------------------

# --------------Read (Display Exercises)--------------------
@app.route("/exercises", methods=["GET"])
def exercises():
    """
    Display all exercises in a table format.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Exercises"
        cursor.execute(query)
        exercises = cursor.fetchall()
        cursor.close()

        return render_template("exercises.html", exercises=exercises)
    except Exception as e:
        print(f"Error fetching exercises: {e}")
        return "Internal Server Error", 500


# --------------Create Exercises---------------------------
@app.route("/create_exercise", methods=["POST"])
def create_exercise():
    """
    Create a new exercise in the database.
    """
    name = request.form.get("name", "").strip()
    exerciseMinutes = request.form.get("exerciseMinutes", "").strip()
    caloriesBurned = request.form.get("caloriesBurned", "").strip()

    if not name or not exerciseMinutes.isdigit() or not caloriesBurned.isdigit():
        flash("All fields are required and exerciseMinutes, caloriesBurned must be numbers.")
        return redirect(url_for('exercises'))

    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Exercises (name, exerciseMinutes, caloriesBurned) VALUES (%s, %s, %s);"
        cursor.execute(query, (name, int(exerciseMinutes), int(caloriesBurned)))
        mysql.connection.commit()
        cursor.close()

        flash(f"Exercise '{name}' added successfully!")
        return redirect(url_for('exercises'))

    except Exception as e:
        print(f"Error creating exercise: {e}")
        flash("Failed to add exercise.")
        return redirect(url_for('exercises'))


# --------------Update Exercises---------------------------
@app.route('/update_exercise/<int:exercise_id>', methods=['POST'])
def update_exercise(exercise_id):
    """
    Update an existing exercise in the database.
    """
    exerciseMinutes = request.form.get("exerciseMinutes", "").strip()
    caloriesBurned = request.form.get("caloriesBurned", "").strip()

    if not exerciseMinutes.isdigit() or not caloriesBurned.isdigit():
        flash("Invalid input. Ensure fields are not empty and numeric.")
        return redirect(url_for('exercises'))

    try:
        cursor = mysql.connection.cursor()
        query = "UPDATE Exercises SET exerciseMinutes=%s, caloriesBurned=%s WHERE exerciseID=%s;"
        cursor.execute(query, (int(exerciseMinutes), int(caloriesBurned), exercise_id))
        mysql.connection.commit()
        cursor.close()

        flash(f"Exercise ID {exercise_id} updated successfully!")
        return redirect(url_for('exercises'))

    except Exception as e:
        print(f"Error updating exercise: {e}")
        flash("Failed to update exercise.")
        return redirect(url_for('exercises'))


# --------------Delete Exercises---------------------------
@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    """
    Delete an exercise from the database.
    """
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Exercises WHERE exerciseID = %s;"
        cursor.execute(query, (exercise_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Exercise deleted", "exercise_id": exercise_id}), 200
    except Exception as e:
        print(f"Error deleting exercise: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



# ------------------ Reset All Tables (Combined Reset) ------------------
@app.route('/reset-all', methods=['POST'])
def reset_all():
    try:
        cmd = f"mysql -h classmysql.engr.oregonstate.edu -u cs340_kimh22 -p'PASSWORD' cs340_kimh22 < /nfs/stak/users/kimh22/public_html/cs340_group39/NutriSphere_admin_panel/database/DDL.sql"

        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        if result.returncode == 0:
            flash("Database successfully reset.")
        else:
            flash(f"Error resetting database: {result.stderr}")

        return redirect(url_for('home'))
    
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('home'))



# --------------------------------------------------
# Start Application
if __name__ == "__main__":
    """
    Runs the Flask application.
    """
    app.run(host="0.0.0.0", port=65216, debug=True)