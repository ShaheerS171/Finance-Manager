"""
Transport Fee Management Screen - Bus Centric
"""

import flet as ft
from database.models import Student, Payment, Bus
from utils.helpers import format_currency, get_current_date, generate_receipt_no

class TransportScreen(ft.Container):
    """Transport fee management screen with Bus Grid and Student Table"""
    
    def __init__(self, db_manager, page):
        super().__init__()
        print("TransportScreen initializing...")
        self.db = db_manager
        self.main_page = page
        
        self.padding = 20
        self.expand = True
        self.current_bus = None # If None, show Bus Grid. If set, show Student Table for this bus.
        
        # UI Components
        self.search_term = ""
        self.search_field = ft.TextField(
            label="Search Student (Name, Father, or Stop)",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            width=300,
            text_size=14,
            content_padding=10
        )
        
        self.bus_grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=300,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
        )
        self.students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Father Name")),
                ft.DataColumn(ft.Text("Stop")),
                ft.DataColumn(ft.Text("Section")),
                ft.DataColumn(ft.Text("Phone")),
                ft.DataColumn(ft.Text("Target"), numeric=True),
                ft.DataColumn(ft.Text("Paid"), numeric=True),
                ft.DataColumn(ft.Text("Pending"), numeric=True),
                ft.DataColumn(ft.Text("Add Payment")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            expand=True,
            column_spacing=10,
            horizontal_lines=ft.border.BorderSide(1, "#EEEEEE"),
            heading_row_color="#f5f5f5",
        )
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the user interface based on state"""
        self.content = ft.Column()
        
        if self.current_bus is None:
            self.show_buses_view()
        else:
            self.show_bus_detail_view()

    def show_buses_view(self):
        """Show grid of buses"""
        print("Showing Buses View")
        self.load_buses()
        
        self.content.controls = [
            # Header
            ft.Row(
                [
                    ft.Icon(ft.Icons.DIRECTIONS_BUS, size=32, color="#2196F3"),
                    ft.Text("Transport Buses", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Add New Bus",
                        icon=ft.Icons.ADD,
                        on_click=self.show_add_bus_dialog,
                        style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            # Grid
            ft.Container(
                content=self.bus_grid,
                expand=True
            ),
            # Bottom Actions
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Bulk Import Students",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=self.show_import_dialog,
                    style=ft.ButtonStyle(bgcolor="#673AB7", color="white")
                ),
                ft.ElevatedButton(
                    "Global Monthly Rollover",
                    icon=ft.Icons.SYNC,
                    on_click=self.confirm_global_rollover,
                    style=ft.ButtonStyle(bgcolor="#E91E63", color="white")
                ),
            ], alignment=ft.MainAxisAlignment.START)
        ]
        
    def show_bus_detail_view(self):
        """Show table of students for selected bus"""
        print(f"Showing Detail View for Bus: {self.current_bus.name}")
        self.load_students()
        
        self.content.controls = [
             # Header with Back Button
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK, 
                        on_click=lambda e: self.navigate_back()
                    ),
                    ft.Text(f"Bus: {self.current_bus.name}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Start New Month",
                        icon=ft.Icons.REPLAY,
                        on_click=self.confirm_new_month,
                        style=ft.ButtonStyle(bgcolor="#FF9800", color="white")
                    ),
                    ft.VerticalDivider(width=10),
                    ft.ElevatedButton(
                        "Export to Excel",
                        icon=ft.Icons.FILE_DOWNLOAD,
                        on_click=lambda e: self.export_bus_details(),
                        style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                    ),
                    ft.ElevatedButton(
                        "Add Student",
                        icon=ft.Icons.PERSON_ADD,
                        on_click=self.show_add_student_dialog,
                         style=ft.ButtonStyle(bgcolor="#2196F3", color="white")
                    )
                ]
            ),
            ft.Divider(),
            # Search bar
            ft.Row([self.search_field]),
            ft.Divider(),
            # Table Container (Scrollable)
             ft.Column(
                [self.students_table],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        ]

    def navigate_back(self):
        """Go back to Buses grid"""
        self.current_bus = None
        self.build_ui()
        self.update()

    def load_buses(self):
        """Load buses from DB and populate grid"""
        self.bus_grid.controls.clear()
        buses = self.db.get_all_buses()
        
        if not buses:
             self.bus_grid.controls.append(
                ft.Container(
                    content=ft.Text("No buses found. Add one to start!"),
                    alignment=ft.Alignment(0, 0)
                )
             )
             return

        for bus in buses:
            # Get stats for this bus (quick calc)
            students = self.db.get_students_by_bus(bus.id)
            total_target = sum(s.target_amount for s in students)
            total_paid = sum(s.paid_amount for s in students)
            
            # Bus Card
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.DIRECTIONS_BUS, color="#FF9800"),
                                title=ft.Text(bus.name, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"Students: {len(students)}"),
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Goal: {format_currency(bus.default_target)}", weight=ft.FontWeight.W_500),
                                    ft.Text(f"Collected: {format_currency(total_paid)}", color="#4CAF50"),
                                    ft.Text(f"Pending: {format_currency(bus.default_target - total_paid)}", color="#F44336"),
                                ])
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("Open", on_click=lambda e, b=bus: self.open_bus(b)),
                                    ft.IconButton(ft.Icons.EDIT, icon_color="#2196F3", on_click=lambda e, b=bus: self.show_edit_bus_dialog(b)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="#F44336", on_click=lambda e, b=bus: self.confirm_delete_bus(b)),
                                ],
                                alignment=ft.MainAxisAlignment.END
                            )
                        ],
                        spacing=10
                    ),
                    padding=10
                ),
                elevation=5,
            )
            self.bus_grid.controls.append(card)

    def open_bus(self, bus):
        """Set current bus and switch view"""
        self.current_bus = bus
        self.search_term = ""
        self.search_field.value = ""
        self.build_ui()
        self.update()

    def on_search_change(self, e):
        """Handle search field changes"""
        self.search_term = e.control.value.lower()
        self.load_students()
        self.update()
        
    def confirm_new_month(self, e):
        """Show confirmation for monthly rollover"""
        def roll(e):
            self.db.reset_bus_payments(self.current_bus.id)
            self.close_dialog(dlg)
            self.load_students()
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"New month started for {self.current_bus.name}"), bgcolor="#4CAF50")
            self.main_page.snack_bar.open = True
            self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Start New Month?"),
            content=ft.Text("This will reset all student payment columns for this bus to zero. All other details stay the same. Proceed?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Reset Payments", on_click=roll, bgcolor="#FF9800", color="white")
            ]
        )
        self.open_dialog(dlg)

    def load_students(self):
        """Load students for current bus into table"""
        self.students_table.rows.clear()
        if not self.current_bus:
            return
            
        students = self.db.get_students_by_bus(self.current_bus.id)
        
        # Apply filter
        if self.search_term:
            students = [
                s for s in students 
                if self.search_term in s.name.lower() or 
                   (s.father_name and self.search_term in s.father_name.lower()) or
                   (s.bus_stop and self.search_term in s.bus_stop.lower())
            ]
        
        for student in students:
            # Row creation
            pending = student.target_amount - student.paid_amount
            
            # Interactive Cells
            
            # Target Update Logic
            def on_target_change(e, s=student):
                try:
                    new_target = float(e.control.value)
                    s.target_amount = new_target
                    self.db.update_student(s)
                    self.load_students() # Refresh to update pending
                    self.main_page.update()
                except ValueError:
                    pass # Ignore invalid

            # Payment Add Logic
            def on_pay_submit(e, s=student):
                try:
                    amount = float(e.control.value)
                    if amount <= 0: return
                    
                    # Create Payment
                    payment = Payment(
                        student_id=s.id,
                        amount=amount,
                        payment_date=get_current_date(),
                        month="Top-up",
                        receipt_no=generate_receipt_no(),
                        notes="Quick Add"
                    )
                    self.db.add_payment(payment)
                    self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Added {format_currency(amount)} to {s.name}"), bgcolor="#4CAF50")
                    self.main_page.snack_bar.open = True
                    self.load_students() # Refresh table
                    self.main_page.update()
                    e.control.value = "" # Clear field (auto done by refresh)
                except ValueError:
                    self.main_page.snack_bar = ft.SnackBar(content=ft.Text("Invalid Amount"), bgcolor="#F44336")
                    self.main_page.snack_bar.open = True
                    self.main_page.update()

            
            self.students_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(student.name)),
                        ft.DataCell(ft.Text(student.father_name or "-")),
                        ft.DataCell(ft.Text(student.bus_stop or "-")),
                        ft.DataCell(ft.Text(student.section or "-")),
                        ft.DataCell(ft.Text(student.phone or "-")),
                        ft.DataCell(ft.Text(format_currency(student.target_amount))),
                        ft.DataCell(ft.Text(format_currency(student.paid_amount), color="#4CAF50")),
                        ft.DataCell(ft.Text(format_currency(pending), color="#F44336")),
                        ft.DataCell(
                            ft.TextField(
                                hint_text="Add",
                                width=70,
                                text_size=12,
                                content_padding=5,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_submit=on_pay_submit
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, icon_size=16, on_click=lambda e, s=student: self.show_edit_student_dialog(s)),
                                ft.IconButton(ft.Icons.DELETE, icon_size=16, icon_color="#F44336", on_click=lambda e, s=student: self.confirm_delete_student(s)),
                            ])
                        ),
                    ]
                )
            )

    # --- DIALOGS ---

    def show_add_bus_dialog(self, e):
        """Dialog to add bus"""
        name_field = ft.TextField(label="Bus/Route Name", autofocus=True)
        target_field = ft.TextField(label="Default Target Amount", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        
        def add_bus(e):
            if not name_field.value: return
            try:
                bus = Bus(name=name_field.value, default_target=float(target_field.value))
                self.db.add_bus(bus)
                self.close_dialog(dlg)
                self.load_buses()
                self.main_page.update()
            except Exception as ex:
                print(ex)

        dlg = ft.AlertDialog(
            title=ft.Text("Add Bus/Route"),
            content=ft.Column([name_field, target_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Add", on_click=add_bus)
            ]
        )
        self.open_dialog(dlg)

    def show_add_student_dialog(self, e):
        """Dialog to add student to current bus"""
        name_field = ft.TextField(label="Student Name", autofocus=True)
        father_field = ft.TextField(label="Father's Name")
        stop_field = ft.TextField(label="Bus Stop")
        section_field = ft.TextField(label="Section", value="A")
        phone_field = ft.TextField(label="Phone")
        paid_field = ft.TextField(label="Initial Payment (Optional)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        
        def add_student(e):
            if not name_field.value: return
            try:
                student = Student(
                    name=name_field.value,
                    father_name=father_field.value,
                    bus_id=self.current_bus.id,
                    bus_stop=stop_field.value,
                    section=section_field.value,
                    phone=phone_field.value,
                    target_amount=self.current_bus.default_target,
                    paid_amount=float(paid_field.value or 0)
                )
                self.db.add_student(student)
                self.close_dialog(dlg)
                self.load_students()
                self.main_page.update()
            except Exception as ex:
                self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {ex}"), bgcolor="#F44336")
                self.main_page.snack_bar.open = True
                self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Add Student to {self.current_bus.name}"),
            content=ft.Column([
                name_field, 
                father_field,
                stop_field,
                ft.Row([section_field, phone_field]),
                paid_field,
                ft.Text(f"Target Fee: {format_currency(self.current_bus.default_target)}", italic=True, color="#666666", size=12),
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Add Student", on_click=add_student, bgcolor="#2196F3", color="white")
            ]
        )
        self.open_dialog(dlg)
        
    def show_edit_bus_dialog(self, bus):
        """Edit bus"""
        name_field = ft.TextField(label="Bus Name", value=bus.name)
        target_field = ft.TextField(label="Default Target", value=str(bus.default_target))
        
        def save(e):
            bus.name = name_field.value
            bus.default_target = float(target_field.value or 0)
            self.db.update_bus(bus)
            self.close_dialog(dlg)
            self.load_buses()
            self.main_page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Edit Bus"),
            content=ft.Column([name_field, target_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Save", on_click=save)
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_bus(self, bus):
        """Delete bus"""
        def delete(e):
            self.db.delete_bus(bus.id)
            self.close_dialog(dlg)
            self.load_buses()
            self.main_page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Delete {bus.name}? Students will be hidden."),
            actions=[
                 ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                 ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    # Reuse existing dialog logic for edit student
    def show_edit_student_dialog(self, student):
         # Similar to Add but pre-filled
        name_field = ft.TextField(label="Name", value=student.name)
        father_field = ft.TextField(label="Father's Name", value=student.father_name or "")
        stop_field = ft.TextField(label="Bus Stop", value=student.bus_stop or "")
        section_field = ft.TextField(label="Section", value=student.section or "")
        phone_field = ft.TextField(label="Phone", value=student.phone or "")
        target_field = ft.TextField(label="Fee Target", value=str(student.target_amount))

        def save(e):
            student.name = name_field.value
            student.father_name = father_field.value
            student.bus_stop = stop_field.value
            student.section = section_field.value
            student.phone = phone_field.value
            student.target_amount = float(target_field.value or 0)
            self.db.update_student(student)
            self.close_dialog(dlg)
            self.load_students()
            self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Student Details"),
            content=ft.Column([
                name_field, 
                father_field,
                stop_field,
                ft.Row([section_field, phone_field]),
                target_field
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Save Changes", on_click=save, bgcolor="#2196F3", color="white")
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_student(self, student):
        def delete(e):
            self.db.delete_student(student.id)
            self.close_dialog(dlg)
            self.load_students()
            self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Delete {student.name}?"),
            actions=[
                 ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                 ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    def export_bus_details(self):
        """Export current bus details and students to Excel"""
        from utils.export import export_students_to_excel
        if not self.current_bus: return
        
        try:
            students = self.db.get_students_by_bus(self.current_bus.id)
            filename = export_students_to_excel(students)
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Exported to {filename}"), bgcolor="#4CAF50")
            self.main_page.snack_bar.open = True
            self.main_page.update()
        except Exception as e:
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Export failed: {str(e)}"), bgcolor="#F44336")
            self.main_page.snack_bar.open = True
            self.main_page.update()


    def show_import_dialog(self, e):
        """Show file picker for bulk import"""
        file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.main_page.overlay.append(file_picker)
        self.main_page.update()
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["csv", "xlsx"])

    def on_file_result(self, e):
        if not e.files: return
        
        file_path = e.files[0].path
        from utils.importer import import_students_from_file
        
        try:
            count = import_students_from_file(file_path, self.db)
            self.load_buses() # Refresh grid
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Successfully imported {count} students!"), bgcolor="#4CAF50")
            self.main_page.snack_bar.open = True
            self.main_page.update()
        except Exception as ex:
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Import failed: {str(ex)}"), bgcolor="#F44336")
            self.main_page.snack_bar.open = True
            self.main_page.update()

    def confirm_global_rollover(self, e):
        """Show confirmation for GLOBAL monthly rollover"""
        def roll(e):
            self.db.reset_all_payments()
            self.close_dialog(dlg)
            self.load_buses()
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text("Global monthly rollover complete! All payments reset."), bgcolor="#4CAF50")
            self.main_page.snack_bar.open = True
            self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Global Monthly Rollover?"),
            content=ft.Text("CRITICAL: This will reset payments for ALL students in ALL buses to zero. This is usually done at the start of a new month. Proceed?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Reset All Payments", on_click=roll, bgcolor="#E91E63", color="white")
            ]
        )
        self.open_dialog(dlg)

    def open_dialog(self, dlg):
        """Open a dialog using overlay"""
        if dlg not in self.main_page.overlay:
            self.main_page.overlay.append(dlg)
        dlg.open = True
        self.main_page.update()

    def close_dialog(self, dialog):
        """Close a dialog"""
        dialog.open = False
        self.main_page.update()
