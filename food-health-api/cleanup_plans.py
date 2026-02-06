from app.database.connection import SessionLocal
from app.models.diet_plan import DietPlan

def cleanup():
    db = SessionLocal()
    try:
        print("Cleaning up AI generated plans...")
        # Delete all AI generated plans to ensure a fresh start with fixed logic
        deleted = db.query(DietPlan).filter(DietPlan.source == "ai_generated").delete()
        db.commit()
        print(f"✅ Successfully deleted {deleted} AI generated plans.")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
