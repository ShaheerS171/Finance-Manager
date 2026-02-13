# QUICK START GUIDE

## Installation (5 minutes)

### Step 1: Install Python Packages
Open terminal in the project folder and run:
```bash
pip install flet openpyxl
```

OR if using pip3:
```bash
pip3 install flet openpyxl
```

### Step 2: Run the App
```bash
python main.py
```

OR if using python3:
```bash
python3 main.py
```

That's it! The app will open in a new window.

## First Time Setup

### Add Your First Student
1. Click on "Transport" in the left sidebar
2. Click the green "+" button
3. Fill in:
   - Student Name
   - Class
   - Phone Number (optional)
   - Monthly Fee (e.g., 500)
   - Target Amount (e.g., 6000 for annual fee)
4. Click "Add Student"

### Record a Payment
1. Find the student in the list
2. Click the green "Payment" icon (₹)
3. Enter payment amount
4. Select month (optional)
5. Click "Add Payment"

### Create an Event
1. Click on "Events" in the left sidebar
2. Click "Add Event"
3. Fill in event details:
   - Event Name (e.g., "Annual Day")
   - Description
   - Target Amount
   - Deadline
4. Click "Create Event"
5. Click on the event to add participants

## Common Tasks

### View Pending Payments
- Go to Dashboard
- Click "View Defaulters"

### Export Data
- Go to Dashboard
- Click "Export Transport Data" for all students
- Or go to Events and export individual events

### Backup Database
- Go to Dashboard
- Click "Backup Database"
- Backup file saved in data/ folder

### Search Students
- Go to Transport screen
- Use the search bar at the top
- Search by name or class

## Keyboard Shortcuts

- Tab: Move to next field
- Enter: Submit form (in dialogs)
- Esc: Close dialog (when available)

## Tips for Your Uncle

1. **Daily Routine**:
   - Open app
   - Go to Transport
   - Record any new payments
   - Check dashboard for pending amounts

2. **End of Month**:
   - View Defaulters list
   - Export data for records
   - Backup database

3. **For Events**:
   - Create event when announced
   - Add all participants
   - Track payments as they come in
   - Export when event is complete

## File Locations

- **Database**: `data/fee_manager.db`
- **Backups**: `data/backup_YYYYMMDD_HHMMSS.db`
- **Exports**: Same folder as the app (where main.py is)

## Troubleshooting

**App won't start?**
- Check if flet is installed: `pip list | grep flet`
- Try: `pip install --upgrade flet`

**Can't find exported files?**
- Look in the same folder where main.py is located

**Database error?**
- Check if `data/` folder exists
- Try creating a backup and restart

## Need Help?

Check the full README.md for detailed documentation.

---

**Remember**: The app works completely offline. No internet required!
