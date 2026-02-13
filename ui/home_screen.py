"""
Home/Dashboard screen
"""

import flet as ft
from ui.components import StatsCard
from utils.helpers import format_currency


class HomeScreen(ft.Container):
    """Dashboard/Home screen with statistics"""
    
    def __init__(self, db_manager, page):
        super().__init__()
        print("HomeScreen.__init__ started")
        self.db = db_manager
        # FIX: Rename self.page to self.main_page to avoid conflict
        self.main_page = page 
        
        self.padding = 20
        self.expand = True
        

        
        # Get statistics
        transport_stats = self.db.get_transport_stats()
        events_stats = self.db.get_events_stats()
        
        # Calculate totals
        total_target = transport_stats['total_target'] + events_stats['total_target']
        total_collected = transport_stats['total_collected'] + events_stats['total_collected']
        total_pending = total_target - total_collected
        
        # Build UI
        # Build UI
        self.content = ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DASHBOARD, size=32, color="#2196F3"),
                            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Overall Statistics
                ft.Text("Overall Statistics", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            StatsCard("Total Target", format_currency(total_target), "", "#2196F3"),
                            StatsCard("Total Collected", format_currency(total_collected), "", "#4CAF50"),
                            StatsCard("Total Pending", format_currency(total_pending), "", "#F44336"),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Transport Statistics (Bus Summaries)
                ft.Text("Bus Performance", size=20, weight=ft.FontWeight.BOLD),
                self.build_bus_summaries(),
                ft.Container(height=20),
                
                # Events Statistics
                ft.Text("Events", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            StatsCard(
                                "Total Events", 
                                str(events_stats['total_events']),
                                "",
                                "#FF9800"
                            ),
                            StatsCard(
                                "Target Amount", 
                                format_currency(events_stats['total_target']),
                                "",
                                "#2196F3"
                            ),
                            StatsCard(
                                "Collected", 
                                format_currency(events_stats['total_collected']),
                                "",
                                "#4CAF50"
                            ),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Quick Actions
                ft.Text("Quick Actions", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                "View Defaulters",
                                icon=ft.Icons.WARNING_AMBER,
                                on_click=lambda e: self.show_defaulters(),
                                style=ft.ButtonStyle(
                                    bgcolor="#F44336",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Export Transport Data",
                                icon=ft.Icons.FILE_DOWNLOAD,
                                on_click=lambda e: self.export_transport_data(),
                                style=ft.ButtonStyle(
                                    bgcolor="#2196F3",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Backup Database",
                                icon=ft.Icons.BACKUP,
                                on_click=lambda e: self.backup_database(),
                                style=ft.ButtonStyle(
                                    bgcolor="#4CAF50",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                        ],
                        spacing=10,
                        wrap=True,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def build_bus_summaries(self):
        """Build cards for each bus"""
        buses = self.db.get_all_buses()
        if not buses:
             return ft.Text("No buses found", color="grey")
        
        cards = []
        for bus in buses:
            students = self.db.get_students_by_bus(bus.id)
            if not students: continue
            
            total = sum(s.target_amount for s in students)
            paid = sum(s.paid_amount for s in students)
            pending = total - paid
            progress = paid / total if total > 0 else 0
            
            cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(bus.name, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(value=progress, color="#4CAF50" if pending == 0 else "#2196F3", bgcolor="#E0E0E0"),
                        ft.Row([
                            ft.Text(f"Coll: {format_currency(paid)}", size=12),
                            ft.Text(f"Pen: {format_currency(pending)}", size=12, color="#F44336" if pending > 0 else "#4CAF50"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    padding=10,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=5,
                    width=200,
                    height=100,
                    bgcolor="white", # Explicit white for card look
                )
            )
        
        return ft.Row(cards, scroll=ft.ScrollMode.HIDDEN, wrap=True)
    
    def show_defaulters(self):
        """Show list of defaulters"""
        from utils.export import export_defaulters_to_excel
        
        defaulters = self.db.get_defaulters()
        
        if not defaulters:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No pending payments!"), bgcolor="#4CAF50")
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Create dialog with defaulters list
        defaulter_cards = []
        for student in defaulters:
            pending = student.target_amount - student.paid_amount
            defaulter_cards.append(
                ft.ListTile(
                    title=ft.Text(f"{student.name} - {student.class_name}"),
                    subtitle=ft.Text(f"Pending: {format_currency(pending)}"),
                    trailing=ft.Text(student.phone or "No phone"),
                )
            )
        
        dlg = ft.AlertDialog(
            title=ft.Text("Students with Pending Payments"),
            content=ft.Container(
                content=ft.Column(defaulter_cards, scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400,
            ),
            actions=[
                ft.TextButton(
                    "Export to Excel",
                    on_click=lambda e: self.export_defaulters(defaulters, dlg)
                ),
                ft.TextButton("Close", on_click=lambda e: self.close_dialog(dlg)),
            ],
        )
        
        self.open_dialog(dlg)
    
    def export_defaulters(self, defaulters, dialog):
        """Export defaulters to Excel"""
        from utils.export import export_defaulters_to_excel
        
        try:
            filename = export_defaulters_to_excel(defaulters)
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Exported to {filename}"), bgcolor="#4CAF50")
            self.page.snack_bar.open = True
            self.page.update()
            self.close_dialog(dialog)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Export failed: {str(e)}"), bgcolor="#F44336")
            self.page.snack_bar.open = True
            self.page.update()
    
    def export_transport_data(self):
        """Export all transport data to Excel"""
        from utils.export import export_students_to_excel, export_payments_to_excel
        
        try:
            students = self.db.get_all_students()
            payments = self.db.get_all_payments()
            
            students_file = export_students_to_excel(students)
            payments_file = export_payments_to_excel(payments)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Exported to {students_file} and {payments_file}"),
                bgcolor="#4CAF50"
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Export failed: {str(e)}"), bgcolor="#F44336")
            self.page.snack_bar.open = True
            self.page.update()
    
    def backup_database(self):
        """Backup the database"""
        from datetime import datetime
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backup_{timestamp}.db"
            
            if self.db.backup_database(backup_path):
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Backup saved to {backup_path}"), bgcolor="#4CAF50")
                self.page.snack_bar.open = True
                self.page.update()
            else:
                raise Exception("Backup failed")
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Backup failed: {str(e)}"), bgcolor="#F44336")
            self.page.snack_bar.open = True
            self.page.update()
    
    def open_dialog(self, dlg):
        """Open a dialog using overlay"""
        if dlg not in self.page.overlay:
            self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()
    
    def refresh(self):
        """Refresh the dashboard"""
        # Recreate the content with updated stats
        transport_stats = self.db.get_transport_stats()
        events_stats = self.db.get_events_stats()
        
        total_target = transport_stats['total_target'] + events_stats['total_target']
        total_collected = transport_stats['total_collected'] + events_stats['total_collected']
        total_pending = total_target - total_collected
        
        # Rebuild content
        self.content = ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DASHBOARD, size=32, color="#2196F3"),
                            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Overall Statistics
                ft.Text("Overall Statistics", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            StatsCard("Total Target", format_currency(total_target), "", "#2196F3"),
                            StatsCard("Total Collected", format_currency(total_collected), "", "#4CAF50"),
                            StatsCard("Total Pending", format_currency(total_pending), "", "#F44336"),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Transport Statistics (Bus Summaries)
                ft.Text("Bus Performance", size=20, weight=ft.FontWeight.BOLD),
                self.build_bus_summaries(),
                ft.Container(height=20),
                
                # Events Statistics
                ft.Text("Events", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            StatsCard(
                                "Total Events", 
                                str(events_stats['total_events']),
                                "",
                                "#FF9800"
                            ),
                            StatsCard(
                                "Target Amount", 
                                format_currency(events_stats['total_target']),
                                "",
                                "#2196F3"
                            ),
                            StatsCard(
                                "Collected", 
                                format_currency(events_stats['total_collected']),
                                "",
                                "#4CAF50"
                            ),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Quick Actions
                ft.Text("Quick Actions", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                "View Defaulters",
                                icon=ft.Icons.WARNING_AMBER,
                                on_click=lambda e: self.show_defaulters(),
                                style=ft.ButtonStyle(
                                    bgcolor="#F44336",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Export Transport Data",
                                icon=ft.Icons.FILE_DOWNLOAD,
                                on_click=lambda e: self.export_transport_data(),
                                style=ft.ButtonStyle(
                                    bgcolor="#2196F3",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Backup Database",
                                icon=ft.Icons.BACKUP,
                                on_click=lambda e: self.backup_database(),
                                style=ft.ButtonStyle(
                                    bgcolor="#4CAF50",
                                    color="white",
                                    padding=20,
                                ),
                            ),
                        ],
                        spacing=10,
                        wrap=True,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.update()
