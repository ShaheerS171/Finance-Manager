"""
Database manager for handling all database operations
"""

import sqlite3
import os
from datetime import datetime
from database.models import Student, Payment, Event, EventParticipant, EventPayment, Bus, PrincipalPayment, TeacherDebt


class DatabaseManager:
    def __init__(self, db_path="data/fee_manager.db"):
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()
        self._cleanup_orphans()
    
    
    def _ensure_database_exists(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Create all necessary tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Buses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                default_target REAL DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                father_name TEXT,
                class_name TEXT,
                section TEXT,
                bus_id INTEGER,
                bus_stop TEXT,
                phone TEXT,
                monthly_fee REAL DEFAULT 0,
                target_amount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bus_id) REFERENCES buses (id)
            )
        ''')
        
        # Migrations for students table
        columns_to_add = [
            ("father_name", "TEXT"),
            ("section", "TEXT"),
            ("bus_stop", "TEXT")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"SELECT {col_name} FROM students LIMIT 1")
            except sqlite3.OperationalError:
                print(f"Migrating students table: adding {col_name} column")
                try:
                    cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Migration failed for {col_name}: {e}")
        
        # Check if students table needs migration (add bus_id)
        try:
            cursor.execute("SELECT bus_id FROM students LIMIT 1")
        except sqlite3.OperationalError:
            print("Migrating students table: adding bus_id column")
            try:
                cursor.execute("ALTER TABLE students ADD COLUMN bus_id INTEGER REFERENCES buses(id)")
            except Exception as e:
                print(f"Migration failed for bus_id: {e}")
        
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                receipt_no TEXT,
                month TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                target_amount REAL DEFAULT 0,
                collected_amount REAL DEFAULT 0,
                deadline TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Event participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                amount_due REAL DEFAULT 0,
                amount_paid REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        
        # Event payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                receipt_no TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES event_participants (id)
            )
        ''')
        
        # Principal payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS principal_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Teacher debt table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_debt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                amount REAL NOT NULL,
                debt_date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def _cleanup_orphans(self):
        """Remove orphaned/legacy data on startup"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Thoroughly delete anything marked as inactive (legacy)
        # Delete payments and participants for inactive events
        cursor.execute('DELETE FROM event_payments WHERE participant_id IN (SELECT id FROM event_participants WHERE event_id IN (SELECT id FROM events WHERE active = 0))')
        cursor.execute('DELETE FROM event_participants WHERE event_id IN (SELECT id FROM events WHERE active = 0)')
        cursor.execute('DELETE FROM events WHERE active = 0')
        
        # Delete payments and students for inactive buses
        cursor.execute('DELETE FROM payments WHERE student_id IN (SELECT id FROM students WHERE bus_id IN (SELECT id FROM buses WHERE active = 0))')
        cursor.execute('DELETE FROM students WHERE bus_id IN (SELECT id FROM buses WHERE active = 0)')
        cursor.execute('DELETE FROM buses WHERE active = 0')
        
        # Delete inactive students
        cursor.execute('DELETE FROM payments WHERE student_id IN (SELECT id FROM students WHERE active = 0)')
        cursor.execute('DELETE FROM students WHERE active = 0')
        
        # Clean up orphaned students/participants with no matching parent
        cursor.execute('DELETE FROM payments WHERE student_id NOT IN (SELECT id FROM students)')
        cursor.execute('DELETE FROM students WHERE bus_id NOT IN (SELECT id FROM buses) AND bus_id IS NOT NULL')
        cursor.execute('DELETE FROM event_payments WHERE participant_id NOT IN (SELECT id FROM event_participants)')
        cursor.execute('DELETE FROM event_participants WHERE event_id NOT IN (SELECT id FROM events)')
        
        conn.commit()
        conn.close()

    # ===== BUS OPERATIONS =====

    def add_bus(self, bus):
        """Add a new bus"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO buses (name, default_target)
            VALUES (?, ?)
        ''', (bus.name, bus.default_target))
        conn.commit()
        bus_id = cursor.lastrowid
        conn.close()
        return bus_id

    def get_all_buses(self):
        """Get all buses"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, default_target, active FROM buses ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        buses = []
        for row in rows:
            bus = Bus(id=row[0], name=row[1], default_target=row[2])
            buses.append(bus)
        return buses

    def get_bus_by_id(self, bus_id):
        """Get bus by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, default_target, active FROM buses WHERE id = ?', (bus_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Bus(id=row[0], name=row[1], default_target=row[2])
        return None

    def update_bus(self, bus):
        """Update bus info"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE buses SET name = ?, default_target = ? WHERE id = ?
        ''', (bus.name, bus.default_target, bus.id))
        conn.commit()
        conn.close()
    
    def delete_bus(self, bus_id):
        """Hard delete bus and its students"""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Delete payments for students of this bus
        cursor.execute('DELETE FROM payments WHERE student_id IN (SELECT id FROM students WHERE bus_id = ?)', (bus_id,))
        # Delete students of this bus
        cursor.execute('DELETE FROM students WHERE bus_id = ?', (bus_id,))
        # Delete the bus
        cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
        conn.commit()
        conn.close()
    
    def get_students_by_bus(self, bus_id):
        """Get students for a specific bus"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, father_name, class_name, section, bus_id, bus_stop, phone, 
                   monthly_fee, target_amount, paid_amount 
            FROM students WHERE bus_id=? ORDER BY name
        ''', (bus_id,))
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                id=row[0], name=row[1], father_name=row[2], class_name=row[3], section=row[4],
                bus_id=row[5], bus_stop=row[6], phone=row[7], monthly_fee=row[8], 
                target_amount=row[9], paid_amount=row[10]
            )
            students.append(student)
        return students

    
    # ===== STUDENT OPERATIONS =====
    
    def add_student(self, student):
        """Add a new student"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, father_name, class_name, section, bus_id, bus_stop, 
                                 phone, monthly_fee, target_amount, paid_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student.name, student.father_name, student.class_name, student.section, 
              student.bus_id, student.bus_stop, student.phone, student.monthly_fee, 
              student.target_amount, student.paid_amount))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id
    
    def get_all_students(self):
        """Get all students"""
        conn = self._get_connection()
        cursor = conn.cursor()
        query = '''SELECT id, name, father_name, class_name, section, bus_id, bus_stop, phone, 
                          monthly_fee, target_amount, paid_amount FROM students'''
        cursor.execute(query + ' ORDER BY class_name, name')
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                id=row[0], name=row[1], father_name=row[2], class_name=row[3], section=row[4],
                bus_id=row[5], bus_stop=row[6], phone=row[7], monthly_fee=row[8], 
                target_amount=row[9], paid_amount=row[10]
            )
            students.append(student)
        return students
    
    def get_student_by_id(self, student_id):
        """Get student by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, father_name, class_name, section, bus_id, bus_stop, phone, 
                   monthly_fee, target_amount, paid_amount 
            FROM students WHERE id = ?
        ''', (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Student(
                id=row[0], name=row[1], father_name=row[2], class_name=row[3], section=row[4],
                bus_id=row[5], bus_stop=row[6], phone=row[7], monthly_fee=row[8], 
                target_amount=row[9], paid_amount=row[10]
            )
        return None
    
    def update_student(self, student):
        """Update student information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students 
            SET name = ?, father_name = ?, class_name = ?, section = ?, bus_id = ?, 
                bus_stop = ?, phone = ?, monthly_fee = ?, target_amount = ?, 
                paid_amount = ?
            WHERE id = ?
        ''', (student.name, student.father_name, student.class_name, student.section, 
              student.bus_id, student.bus_stop, student.phone, student.monthly_fee,
              student.target_amount, student.paid_amount, student.id))
        conn.commit()
        conn.close()
    
    def delete_student(self, student_id):
        """Hard delete a student and their payments"""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Delete payments for this student
        cursor.execute('DELETE FROM payments WHERE student_id = ?', (student_id,))
        # Delete the student
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()
    
    def search_students(self, search_term):
        """Search students by name, father's name, or class"""
        conn = self._get_connection()
        cursor = conn.cursor()
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT id, name, father_name, class_name, section, bus_id, bus_stop, phone, 
                   monthly_fee, target_amount, paid_amount 
            FROM students 
            WHERE (name LIKE ? OR father_name LIKE ? OR class_name LIKE ? OR bus_stop LIKE ?)
            ORDER BY class_name, name
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                id=row[0], name=row[1], father_name=row[2], class_name=row[3], section=row[4],
                bus_id=row[5], bus_stop=row[6], phone=row[7], monthly_fee=row[8], 
                target_amount=row[9], paid_amount=row[10]
            )
            students.append(student)
        return students
    
    def get_defaulters(self):
        """Get list of students who haven't paid (paid_amount < target_amount)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, father_name, class_name, section, bus_id, bus_stop, phone, 
                   monthly_fee, target_amount, paid_amount 
            FROM students 
            WHERE paid_amount < target_amount
            ORDER BY class_name, name
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                id=row[0], name=row[1], father_name=row[2], class_name=row[3], section=row[4],
                bus_id=row[5], bus_stop=row[6], phone=row[7], monthly_fee=row[8], 
                target_amount=row[9], paid_amount=row[10]
            )
            students.append(student)
        return students
    
    def reset_bus_payments(self, bus_id):
        """Reset paid_amount to 0 for all students in a bus (for new month)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students 
            SET paid_amount = 0 
            WHERE bus_id = ?
        ''', (bus_id,))
        conn.commit()
        conn.close()
        return True

    def reset_all_payments(self):
        """Reset paid_amount to 0 for ALL students in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET paid_amount = 0')
        conn.commit()
        conn.close()
        return True
    
    # ===== PAYMENT OPERATIONS =====
    
    def add_payment(self, payment):
        """Add a new payment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (student_id, amount, payment_date, receipt_no, month, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (payment.student_id, payment.amount, payment.payment_date, 
              payment.receipt_no, payment.month, payment.notes))
        
        # Update student's paid amount
        cursor.execute('''
            UPDATE students 
            SET paid_amount = paid_amount + ?
            WHERE id = ?
        ''', (payment.amount, payment.student_id))
        
        conn.commit()
        payment_id = cursor.lastrowid
        conn.close()
        return payment_id
    
    def get_student_payments(self, student_id):
        """Get all payments for a student"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, student_id, amount, payment_date, receipt_no, month, notes 
            FROM payments 
            WHERE student_id = ?
            ORDER BY payment_date DESC
        ''', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        
        payments = []
        for row in rows:
            payment = Payment(
                id=row[0], student_id=row[1], amount=row[2], payment_date=row[3],
                receipt_no=row[4], month=row[5], notes=row[6]
            )
            payments.append(payment)
        return payments
    
    def get_all_payments(self):
        """Get all payments"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.student_id, p.amount, p.payment_date, p.receipt_no, p.month, p.notes, s.name, s.class_name 
            FROM payments p
            JOIN students s ON p.student_id = s.id
            ORDER BY p.payment_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    # ===== EVENT OPERATIONS =====
    
    def add_event(self, event):
        """Add a new event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (name, description, target_amount, collected_amount, deadline)
            VALUES (?, ?, ?, ?, ?)
        ''', (event.name, event.description, event.target_amount, 
              event.collected_amount, event.deadline))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id
    
    def get_all_events(self):
        """Get all events with dynamically calculated collected_amount"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Calculate collected_amount on the fly from participants
        query = '''
            SELECT 
                e.id, e.name, e.description, e.target_amount, 
                IFNULL(SUM(p.amount_paid), 0) as collected_amount,
                e.deadline, e.active 
            FROM events e
            LEFT JOIN event_participants p ON e.id = p.event_id
            GROUP BY e.id 
            ORDER BY e.deadline DESC, e.created_at DESC
        '''
        cursor.execute(query)
            
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event = Event(
                id=row[0], name=row[1], description=row[2], target_amount=row[3],
                collected_amount=row[4], deadline=row[5]
            )
            events.append(event)
        return events
    
    def get_event_by_id(self, event_id):
        """Get event by ID with dynamically calculated collected_amount"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                e.id, e.name, e.description, e.target_amount, 
                IFNULL(SUM(p.amount_paid), 0) as collected_amount,
                e.deadline
            FROM events e
            LEFT JOIN event_participants p ON e.id = p.event_id
            WHERE e.id = ?
            GROUP BY e.id
        ''', (event_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Event(
                id=row[0], name=row[1], description=row[2], target_amount=row[3],
                collected_amount=row[4], deadline=row[5]
            )
        return None
    
    def update_event(self, event):
        """Update event information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE events 
            SET name = ?, description = ?, target_amount = ?, 
                collected_amount = ?, deadline = ?
            WHERE id = ?
        ''', (event.name, event.description, event.target_amount,
              event.collected_amount, event.deadline, event.id))
        conn.commit()
        conn.close()
    
    def delete_event(self, event_id):
        """Hard delete an event and its participants/payments"""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Delete payments for participants of this event
        cursor.execute('DELETE FROM event_payments WHERE participant_id IN (SELECT id FROM event_participants WHERE event_id = ?)', (event_id,))
        # Delete participants of this event
        cursor.execute('DELETE FROM event_participants WHERE event_id = ?', (event_id,))
        # Delete the event
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()
    
    # ===== EVENT PARTICIPANT OPERATIONS =====
    
    def add_event_participant(self, participant):
        """Add a new event participant"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_participants (event_id, name, phone, amount_due, amount_paid)
            VALUES (?, ?, ?, ?, ?)
        ''', (participant.event_id, participant.name, participant.phone,
              participant.amount_due, participant.amount_paid))
        conn.commit()
        participant_id = cursor.lastrowid
        conn.close()
        return participant_id
    
    def get_event_participants(self, event_id):
        """Get all participants for an event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, event_id, name, phone, amount_due, amount_paid 
            FROM event_participants 
            WHERE event_id = ?
            ORDER BY name
        ''', (event_id,))
        rows = cursor.fetchall()
        conn.close()
        
        participants = []
        for row in rows:
            participant = EventParticipant(
                id=row[0], event_id=row[1], name=row[2], phone=row[3],
                amount_due=row[4], amount_paid=row[5]
            )
            participants.append(participant)
        return participants
    
    def update_event_participant(self, participant):
        """Update event participant information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE event_participants 
            SET name = ?, phone = ?, amount_due = ?, amount_paid = ?
            WHERE id = ?
        ''', (participant.name, participant.phone, participant.amount_due,
              participant.amount_paid, participant.id))
        conn.commit()
        conn.close()
    
    def delete_event_participant(self, participant_id):
        """Delete an event participant and their payments"""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Delete payments first
        cursor.execute('DELETE FROM event_payments WHERE participant_id = ?', (participant_id,))
        # Delete the participant
        cursor.execute('DELETE FROM event_participants WHERE id = ?', (participant_id,))
        conn.commit()
        conn.close()
    
    # ===== EVENT PAYMENT OPERATIONS =====
    
    def add_event_payment(self, payment):
        """Add a new event payment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_payments (participant_id, amount, payment_date, receipt_no, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (payment.participant_id, payment.amount, payment.payment_date,
              payment.receipt_no, payment.notes))
        
        # Update participant's paid amount
        cursor.execute('''
            UPDATE event_participants 
            SET amount_paid = amount_paid + ?
            WHERE id = ?
        ''', (payment.amount, payment.participant_id))
        
        conn.commit()
        payment_id = cursor.lastrowid
        conn.close()
        return payment_id
    
    def get_participant_payments(self, participant_id):
        """Get all payments for a participant"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, participant_id, amount, payment_date, receipt_no, notes 
            FROM event_payments 
            WHERE participant_id = ?
            ORDER BY payment_date DESC
        ''', (participant_id,))
        rows = cursor.fetchall()
        conn.close()
        
        payments = []
        for row in rows:
            payment = EventPayment(
                id=row[0], participant_id=row[1], amount=row[2], payment_date=row[3],
                receipt_no=row[4], notes=row[5]
            )
            payments.append(payment)
        return payments
    
    def get_transport_stats(self):
        """Get transport fee statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total target is the sum of goals of all active buses
        # Total collected is the sum of payments from all students in active buses
        cursor.execute('''
            SELECT 
                (SELECT SUM(default_target) FROM buses) as total_target,
                SUM(s.paid_amount) as total_collected,
                COUNT(s.id) as total_students
            FROM students s
            INNER JOIN buses b ON s.bus_id = b.id
        ''')
        row = cursor.fetchone()
        conn.close()
        
        target = row[0] or 0.0
        collected = row[1] or 0.0
        
        return {
            'total_students': row[2] or 0,
            'total_target': target,
            'total_collected': collected,
            'total_pending': max(0, target - collected)
        }
    
    def get_events_stats(self):
        """Get events statistics with dynamically calculated totals"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                (SELECT COUNT(*) FROM events) as total_events,
                (SELECT SUM(target_amount) FROM events) as total_target,
                IFNULL(SUM(p.amount_paid), 0) as total_collected
            FROM events e
            LEFT JOIN event_participants p ON e.id = p.event_id
        ''')
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_events': row[0] or 0,
            'total_target': row[1] or 0.0,
            'total_collected': row[2] or 0.0
        }
    
    # ===== PRINCIPAL PAYMENT OPERATIONS =====
    
    def add_principal_payment(self, payment):
        """Add a new principal payment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO principal_payments (amount, payment_date, notes)
            VALUES (?, ?, ?)
        ''', (payment.amount, payment.payment_date, payment.notes))
        conn.commit()
        payment_id = cursor.lastrowid
        conn.close()
        return payment_id
    
    def get_all_principal_payments(self):
        """Get all principal payments"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, amount, payment_date, notes 
            FROM principal_payments 
            ORDER BY payment_date DESC, created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        payments = []
        for row in rows:
            payment = PrincipalPayment(
                id=row[0], amount=row[1], payment_date=row[2], notes=row[3]
            )
            payments.append(payment)
        return payments
    
    def update_principal_payment(self, payment):
        """Update a principal payment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE principal_payments 
            SET amount = ?, payment_date = ?, notes = ?
            WHERE id = ?
        ''', (payment.amount, payment.payment_date, payment.notes, payment.id))
        conn.commit()
        conn.close()
    
    def delete_principal_payment(self, payment_id):
        """Delete a principal payment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM principal_payments WHERE id = ?', (payment_id,))
        conn.commit()
        conn.close()
    
    def get_principal_stats(self):
        """Get total paid to principal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(amount), COUNT(id) FROM principal_payments')
        row = cursor.fetchone()
        conn.close()
        return {
            'total_paid': row[0] or 0.0,
            'payment_count': row[1] or 0
        }
    
    # ===== BACKUP =====
    
    def backup_database(self, backup_path):
        """Create a backup of the database"""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False
    
    def restore_database(self, backup_path):
        """Restore database from backup"""
        import shutil
        try:
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False
    
    # ===== TEACHER DEBT OPERATIONS =====
    
    def add_teacher_debt(self, debt):
        """Add a new teacher debt record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO teacher_debt (teacher_name, amount, debt_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (debt.teacher_name, debt.amount, debt.debt_date, debt.notes))
        conn.commit()
        debt_id = cursor.lastrowid
        conn.close()
        return debt_id
    
    def get_all_teacher_debt(self):
        """Get all teacher debt records"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, teacher_name, amount, debt_date, notes FROM teacher_debt ORDER BY debt_date DESC')
        rows = cursor.fetchall()
        conn.close()
        
        debts = []
        for row in rows:
            debts.append(TeacherDebt(id=row[0], teacher_name=row[1], amount=row[2], debt_date=row[3], notes=row[4]))
        return debts
    
    def update_teacher_debt(self, debt):
        """Update teacher debt record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE teacher_debt 
            SET teacher_name = ?, amount = ?, debt_date = ?, notes = ?
            WHERE id = ?
        ''', (debt.teacher_name, debt.amount, debt.debt_date, debt.notes, debt.id))
        conn.commit()
        conn.close()
    
    def delete_teacher_debt(self, debt_id):
        """Delete teacher debt record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM teacher_debt WHERE id = ?', (debt_id,))
        conn.commit()
        conn.close()
    
    def get_teacher_debt_stats(self):
        """Get summary stats for teacher debt"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(amount), COUNT(id) FROM teacher_debt')
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_debt': row[0] if row[0] else 0.0,
            'debt_count': row[1] if row[1] else 0
        }
