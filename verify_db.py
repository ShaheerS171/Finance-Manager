
import sqlite3
from database.db_manager import DatabaseManager
from database.models import Bus, Student

def test_db():
    print("Initializing DatabaseManager...")
    db = DatabaseManager()
    
    print("Checking for 'buses' table...")
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buses'")
    if cursor.fetchone():
        print("PASS: 'buses' table exists.")
    else:
        print("FAIL: 'buses' table missing.")
        
    print("Checking for 'bus_id' in 'students' table...")
    cursor.execute("PRAGMA table_info(students)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'bus_id' in columns:
        print("PASS: 'bus_id' column exists.")
    else:
        print(f"FAIL: 'bus_id' missing. Columns: {columns}")
        
    # Test Adding Bus
    print("Testing Add Bus...")
    bus_name = "Test Bus A"
    bus = Bus(name=bus_name, default_target=5000)
    bus_id = db.add_bus(bus)
    print(f"Added Bus ID: {bus_id}")
    
    # Verify
    saved_bus = db.get_bus_by_id(bus_id)
    if saved_bus and saved_bus.name == bus_name:
         print("PASS: Bus retrieval working")
    else:
         print("FAIL: Bus retrieval failed")

    # Clean up
    # db.delete_bus(bus_id) # Keep for UI testing if needed

if __name__ == "__main__":
    test_db()
