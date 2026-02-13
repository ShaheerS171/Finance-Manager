# Transport Fee Manager

A comprehensive fee management system for tracking transport fees and event collections.

## Features

### 🚌 Transport Fee Management
- Add/edit/delete students
- Track monthly fees and payments
- Set target amounts for each student
- View payment history
- Search students by name or class
- Identify students with pending payments
- Export data to Excel

### 🎉 Event Management
- Create and manage multiple events
- Add participants to events
- Track event budgets and collections
- Set deadlines for events
- Partial payment tracking
- Export event data to Excel

### 📊 Dashboard
- Overview of all collections
- Transport fees statistics
- Events statistics
- Quick actions (view defaulters, export data, backup)

### 💾 Data Management
- SQLite database (no server required)
- Backup and restore functionality
- Export to Excel spreadsheets
- Payment history with receipt numbers

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Install the required packages:
```bash
pip install flet openpyxl
```

2. Run the application:
```bash
python main.py
```

That's it! The database will be created automatically on first run.

## Usage

### Running on Desktop
```bash
python main.py
```

### Running on Mobile (Android)

To run on Android, you'll need to package the app:

1. Install flet build tools:
```bash
pip install flet
```

2. Package the app:
```bash
flet build apk
```

This will create an APK file that can be installed on Android devices.

## Project Structure

```
transport-fee-manager/
│
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── database/              # Database layer
│   ├── db_manager.py     # Database operations
│   └── models.py         # Data models
│
├── ui/                   # User interface
│   ├── home_screen.py    # Dashboard
│   ├── transport_screen.py # Transport management
│   ├── events_screen.py  # Events management
│   └── components.py     # Reusable UI components
│
├── utils/                # Utilities
│   ├── helpers.py       # Helper functions
│   └── export.py        # Excel export functionality
│
└── data/                # Data storage
    └── fee_manager.db   # SQLite database (auto-created)
```

## How to Use

### Dashboard
- View overall statistics for transport and events
- Quick access to defaulters list
- Export all data
- Backup database

### Transport Fees
1. Click "Add Student" to add a new student
2. Click on a student card to:
   - View details and payment history
   - Add payment
   - Edit student information
   - Delete student
3. Use the search bar to find students quickly

### Events
1. Click "Add Event" to create a new event
2. Click on an event card to:
   - View event details
   - Add participants
   - Record payments
   - Export event data
   - Edit or delete event

## Tips

### For Your Uncle
- **Regular Backups**: Use the "Backup Database" button regularly
- **Receipt Numbers**: The app auto-generates receipt numbers for tracking
- **Monthly Tracking**: Use the month field when recording transport payments
- **Export Data**: Export to Excel for official records or printing
- **Search Function**: Quickly find students using the search bar
- **Defaulters List**: Regularly check who hasn't paid using the dashboard

### Data Safety
- The database is stored in the `data/` folder
- Create regular backups using the backup button
- Exported Excel files are saved in the same folder as the app

## Troubleshooting

### Database Issues
If you encounter database errors:
1. Check if the `data/` folder exists
2. Make sure you have write permissions
3. Try restoring from a backup

### App Won't Start
1. Ensure Python 3.7+ is installed: `python3 --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Try running from terminal to see error messages

### Export Not Working
1. Make sure openpyxl is installed: `pip install openpyxl`
2. Check file permissions in the app folder

## Future Enhancements

Possible features for future versions:
- SMS reminders for pending payments
- Multi-year data tracking
- Charts and graphs
- Receipt printing
- Cloud sync (optional)
- Multiple clerks/users

## Support

For issues or questions, check:
1. This README file
2. Python error messages in the terminal
3. Database backup functionality to restore data

## License

This is a personal project created for managing transport fees and events.

---

**Version:** 1.0  
**Created:** 2024  
**For:** School/Institution Fee Management
# Finance-Manager
