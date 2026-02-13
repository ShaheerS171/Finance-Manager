"""
Database models and schema definitions
"""

class Bus:
    """Model for a transport bus/route"""
    def __init__(self, id=None, name="", default_target=0.0):
        self.id = id
        self.name = name
        self.default_target = default_target

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'default_target': self.default_target
        }

class Student:
    """Model for transport student"""
    def __init__(self, id=None, name="", father_name="", class_name="", section="", bus_id=None, 
                 bus_stop="", phone="", monthly_fee=0.0, target_amount=0.0, paid_amount=0.0):
        self.id = id
        self.name = name
        self.father_name = father_name
        self.class_name = class_name
        self.section = section
        self.bus_id = bus_id
        self.bus_stop = bus_stop
        self.phone = phone
        self.monthly_fee = monthly_fee
        self.target_amount = target_amount
        self.paid_amount = paid_amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'father_name': self.father_name,
            'class_name': self.class_name,
            'section': self.section,
            'bus_id': self.bus_id,
            'bus_stop': self.bus_stop,
            'phone': self.phone,
            'monthly_fee': self.monthly_fee,
            'target_amount': self.target_amount,
            'paid_amount': self.paid_amount
        }


class Payment:
    """Model for payment transaction"""
    def __init__(self, id=None, student_id=None, amount=0.0, payment_date="", 
                 receipt_no="", month="", notes=""):
        self.id = id
        self.student_id = student_id
        self.amount = amount
        self.payment_date = payment_date
        self.receipt_no = receipt_no
        self.month = month
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'receipt_no': self.receipt_no,
            'month': self.month,
            'notes': self.notes
        }


class Event:
    """Model for event"""
    def __init__(self, id=None, name="", description="", target_amount=0.0, 
                 collected_amount=0.0, deadline=""):
        self.id = id
        self.name = name
        self.description = description
        self.target_amount = target_amount
        self.collected_amount = collected_amount
        self.deadline = deadline
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_amount': self.target_amount,
            'collected_amount': self.collected_amount,
            'deadline': self.deadline
        }


class EventParticipant:
    """Model for event participant"""
    def __init__(self, id=None, event_id=None, name="", phone="", 
                 amount_due=0.0, amount_paid=0.0):
        self.id = id
        self.event_id = event_id
        self.name = name
        self.phone = phone
        self.amount_due = amount_due
        self.amount_paid = amount_paid
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'name': self.name,
            'phone': self.phone,
            'amount_due': self.amount_due,
            'amount_paid': self.amount_paid
        }


class EventPayment:
    """Model for event payment transaction"""
    def __init__(self, id=None, participant_id=None, amount=0.0, 
                 payment_date="", receipt_no="", notes=""):
        self.id = id
        self.participant_id = participant_id
        self.amount = amount
        self.payment_date = payment_date
        self.receipt_no = receipt_no
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'receipt_no': self.receipt_no,
            'notes': self.notes
        }

class PrincipalPayment:
    """Model for payments made to the principal/owner"""
    def __init__(self, id=None, amount=0.0, payment_date="", notes=""):
        self.id = id
        self.amount = amount
        self.payment_date = payment_date
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'notes': self.notes
        }

class TeacherDebt:
    """Model for debt given to teachers"""
    def __init__(self, id=None, teacher_name="", amount=0.0, debt_date="", notes=""):
        self.id = id
        self.teacher_name = teacher_name
        self.amount = amount
        self.debt_date = debt_date
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'teacher_name': self.teacher_name,
            'amount': self.amount,
            'debt_date': self.debt_date,
            'notes': self.notes
        }
