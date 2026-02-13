"""
Helper utility functions
"""

from datetime import datetime


def format_currency(amount):
    """Format amount as currency"""
    return f"Rs. {amount:,.2f}"


def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime():
    """Get current datetime as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_month():
    """Get current month in format like 'January 2024'"""
    return datetime.now().strftime("%B %Y")


def format_date(date_str):
    """Format date string to readable format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")
    except:
        return date_str


def validate_phone(phone):
    """Basic phone number validation"""
    if not phone:
        return True
    # Remove spaces and dashes
    cleaned = phone.replace(" ", "").replace("-", "")
    return cleaned.isdigit() and len(cleaned) >= 10


def generate_receipt_no(prefix="RCP"):
    """Generate a receipt number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}{timestamp}"


def calculate_pending(target, paid):
    """Calculate pending amount"""
    return max(0, target - paid)


def get_payment_status(target, paid):
    """Get payment status"""
    if paid >= target:
        return "Paid"
    elif paid > 0:
        return "Partial"
    else:
        return "Pending"


def get_months_list():
    """Get list of months for the current year"""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    current_year = datetime.now().year
    return [f"{month} {current_year}" for month in months]
