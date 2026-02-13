import csv
import openpyxl
from database.models import Student

def import_students_from_file(file_path, db_manager):
    """
    Imports students from CSV or Excel.
    Expected columns: Name, Father Name, Class, Section, Bus, Stop, Phone, Monthly Fee
    """
    students_to_add = []
    
    # Load all buses for mapping names to IDs
    buses = db_manager.get_all_buses()
    bus_map = {b.name.lower(): b.id for b in buses}
    
    if file_path.endswith('.csv'):
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                students_to_add.append(parse_row(row, bus_map, db_manager))
    elif file_path.endswith('.xlsx'):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data = dict(zip(headers, row))
            students_to_add.append(parse_row(data, bus_map, db_manager))
            
    # Remove None values (failed parses)
    students_to_add = [s for s in students_to_add if s is not None]
    
    count = 0
    for s in students_to_add:
        try:
            db_manager.add_student(s)
            count += 1
        except Exception as e:
            print(f"Error adding student {s.name}: {e}")
            
    return count

def parse_row(row, bus_map, db_manager):
    """Helper to parse a single row from file row dict"""
    try:
        name = row.get('Name', '').strip()
        if not name: return None
        
        bus_name = row.get('Bus', '').strip()
        bus_id = bus_map.get(bus_name.lower())
        
        # If bus doesn't exist, maybe create it? 
        # For simplicity, we skip or use a default. Let's create it if it doesn't exist.
        if bus_name and not bus_id:
            from database.models import Bus
            new_bus = Bus(name=bus_name, default_target=0)
            bus_id = db_manager.add_bus(new_bus)
            bus_map[bus_name.lower()] = bus_id
            
        monthly_fee = float(row.get('Monthly Fee', 0) or 0)
        
        return Student(
            name=name,
            father_name=row.get('Father Name', ''),
            class_name=row.get('Class', ''),
            section=row.get('Section', ''),
            bus_id=bus_id,
            bus_stop=row.get('Stop', ''),
            phone=row.get('Phone', ''),
            monthly_fee=monthly_fee,
            target_amount=monthly_fee, # Initial target = monthly fee
            paid_amount=0
        )
    except Exception as e:
        print(f"Row parse error: {e}")
        return None
