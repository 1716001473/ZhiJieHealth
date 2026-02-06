import sqlite3
import os

DB_PATH = "food_health.db"

def migrate():
    print(f"Checking database at {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check User table
    print("Checking User table...")
    cursor.execute("PRAGMA table_info(user)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "health_goal" not in columns:
        print("Adding health_goal to user...")
        cursor.execute("ALTER TABLE user ADD COLUMN health_goal VARCHAR(50) DEFAULT 'maintain'")
    
    if "dietary_preferences" not in columns:
        print("Adding dietary_preferences to user...")
        cursor.execute("ALTER TABLE user ADD COLUMN dietary_preferences TEXT DEFAULT ''")

    # 2. Check MealRecord table
    print("Checking MealRecord table...")
    try:
        cursor.execute("PRAGMA table_info(meal_record)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "data_source" not in columns:
            print("Adding data_source to meal_record...")
            cursor.execute("ALTER TABLE meal_record ADD COLUMN data_source VARCHAR(20) DEFAULT 'database'")
            
        # Check newly added snapshot columns if they are missing
        if "per_100g_calories" not in columns:
             print("Adding per_100g_calories to meal_record...")
             cursor.execute("ALTER TABLE meal_record ADD COLUMN per_100g_calories FLOAT DEFAULT 0")
             cursor.execute("ALTER TABLE meal_record ADD COLUMN per_100g_protein FLOAT DEFAULT 0")
             cursor.execute("ALTER TABLE meal_record ADD COLUMN per_100g_fat FLOAT DEFAULT 0")
             cursor.execute("ALTER TABLE meal_record ADD COLUMN per_100g_carb FLOAT DEFAULT 0")

    except Exception as e:
        print(f"Error checking meal_record: {e}")

    # 3. Check DietPlan tables (Create if not exist is handled by app startup, but good to check)
    # We rely on app startup for new tables.

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
