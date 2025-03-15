from flask import Flask, render_template, request, json, redirect, url_for, jsonify, flash
from flask_mysqldb import MySQL
import os

# Citation for the following function:
# Date: 02/27/2025  (Update to the date you copied/used it)
# Originality: Adapted
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app
# Description: Adapted from the OSU CS340 Flask Starter App for database connections and routing.


app = Flask(__name__)
app.secret_key = "secret key"

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
            query = "DELETE FROM DailyTracker WHERE dailyTrackerID = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (tracker_id,))
            mysql.connection.commit()
            cur.close()

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
@app.route("/update_exercise/<int:exercise_id>", methods=["POST"])
def update_exercise(exercise_id):
    """
    Update an existing exercise in the database.
    """
    name = request.form.get("name", "").strip()
    exerciseMinutes = request.form.get("exerciseMinutes", "").strip()
    caloriesBurned = request.form.get("caloriesBurned", "").strip()

    if not name or not exerciseMinutes.isdigit() or not caloriesBurned.isdigit():
        flash("Invalid input. Ensure fields are not empty and exerciseMinutes, caloriesBurned are numbers.")
        return redirect(url_for('exercises'))

    try:
        cursor = mysql.connection.cursor()
        query = "UPDATE Exercises SET name=%s, exerciseMinutes=%s, caloriesBurned=%s WHERE exerciseID=%s;"
        cursor.execute(query, (name, int(exerciseMinutes), int(caloriesBurned), exercise_id))
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
        print(f"❌ Error deleting exercise: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



# ------------------ Reset Users Table ------------------
@app.route('/reset-users', methods=['POST'])
def reset_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Users;")
        cursor.execute("ALTER TABLE Users AUTO_INCREMENT = 1;")
        cursor.execute("""
            INSERT INTO Users (username, email, dailyCalorieGoal) VALUES
            ('Tyler', 'tyler@gmail.com', 2400),
            ('Jane', 'jane@yahoo.com', 2000),
            ('Alex', 'alex@hotmail.com', 2200);
        """)
    
        mysql.connection.commit()
        cursor.close()

        flash("Users table reset and default users added.")
        return redirect(url_for('users'))  # Redirect back to the Users page

    except Exception as e:
        print("Error resetting Users table:", e)
        flash("Failed to reset Users table.")
        return redirect(url_for('users'))


# ------------------ Reset Exercises Table ------------------
@app.route('/reset-exercises', methods=['POST'])
def reset_exercises():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Exercises;")
        cursor.execute("ALTER TABLE Exercises AUTO_INCREMENT = 1;")
        cursor.execute("""
            INSERT INTO Exercises (name, exerciseMinutes, caloriesBurned) VALUES
            ('Elliptical', 30, 250),
            ('Hiking', 120, 600),
            ('Swimming', 30, 300),
            ('Pickleball', 60, 400),
            ('Weight Lifting', 60, 150);
        """)
        mysql.connection.commit()
        cursor.close()

        flash("Exercises table reset and default exercises added.")
        return redirect(url_for('exercises'))  # Redirect back to the Exercises page

    except Exception as e:
        print("Error resetting Exercises table:", e)
        flash("Failed to reset Exercises table.")
        return redirect(url_for('exercises'))

# --------------------------------------------------
# Start Application
if __name__ == "__main__":
    """
    Runs the Flask application.
    """
    app.run(host="0.0.0.0", port=65216, debug=True)