"""
Teacher Debt Tracking Screen
- Table for viewing/editing/deleting teacher debt
- Totals card for summary
"""

import flet as ft
from database.models import TeacherDebt
from utils.helpers import format_currency, get_current_date

class TeacherDebtScreen(ft.Container):
    """Screen for tracking debt given to teachers"""
    
    def __init__(self, db_manager, page):
        super().__init__()
        self.db = db_manager
        self.main_page = page
        
        self.padding = 20
        self.expand = True
        
        # UI Components
        self.total_amount_text = ft.Text("PKR 0", size=32, weight=ft.FontWeight.BOLD, color="#F44336")
        self.debt_count_text = ft.Text("0 records found", size=14, color="#666666")
        
        self.total_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total Outstanding Teacher Debt", size=16, weight=ft.FontWeight.BOLD),
                    self.total_amount_text,
                    self.debt_count_text,
                ]),
                padding=20,
            ),
            elevation=5
        )
        
        self.debt_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Teacher Name")),
                ft.DataColumn(ft.Text("Amount"), numeric=True),
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Notes")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            expand=True,
            column_spacing=20,
            horizontal_lines=ft.border.BorderSide(1, "#EEEEEE"),
            heading_row_color="#f5f5f5",
        )
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI layout"""
        self.load_data()
        
        self.content = ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.HANDSHAKE, size=32, color="#F44336"),
                ft.Text("Teacher Debt Records", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add Debt Record",
                    icon=ft.Icons.ADD,
                    on_click=self.show_add_debt_dialog,
                    style=ft.ButtonStyle(bgcolor="#F44336", color="white")
                ),
                ft.VerticalDivider(width=10),
                ft.ElevatedButton(
                    "Export to Excel",
                    icon=ft.Icons.FILE_DOWNLOAD,
                    on_click=lambda e: self.export_debt_list(),
                    style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            # Stats Card
            ft.Row([self.total_card], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(),
            
            # Table Container (Scrollable)
            ft.Text("Debt History", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([self.debt_table], scroll=ft.ScrollMode.AUTO),
                expand=True,
                border=ft.border.all(1, "#EEEEEE"),
                border_radius=10,
                padding=10,
                bgcolor="white"
            )
        ])

    def load_data(self, update_ui=False):
        """Load debt records and update summary"""
        # Load summary
        stats = self.db.get_teacher_debt_stats()
        self.total_amount_text.value = format_currency(stats['total_debt'])
        self.debt_count_text.value = f"{stats['debt_count']} records recorded"
        
        # Load table
        self.debt_table.rows.clear()
        debts = self.db.get_all_teacher_debt()
        
        for d in debts:
            self.debt_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(d.teacher_name, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(format_currency(d.amount), weight=ft.FontWeight.BOLD, color="#F44336")),
                        ft.DataCell(ft.Text(d.debt_date)),
                        ft.DataCell(ft.Text(d.notes or "-")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, icon_color="#2196F3", on_click=lambda e, debt=d: self.show_edit_debt_dialog(debt)),
                                ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="#F44336", on_click=lambda e, debt=d: self.confirm_delete_debt(debt)),
                            ])
                        ),
                    ]
                )
            )
        
        if update_ui:
            try:
                self.update()
            except:
                pass

    # --- DIALOGS ---

    def show_add_debt_dialog(self, e):
        """Dialog to add teacher debt"""
        teacher_field = ft.TextField(label="Teacher Name", autofocus=True)
        amount_field = ft.TextField(label="Amount Given", keyboard_type=ft.KeyboardType.NUMBER)
        date_field = ft.TextField(label="Date (YYYY-MM-DD)", value=get_current_date())
        notes_field = ft.TextField(label="Notes (Optional)", multiline=True, min_lines=2)
        
        def add(e):
            if not teacher_field.value or not amount_field.value: return
            try:
                d = TeacherDebt(
                    teacher_name=teacher_field.value,
                    amount=float(amount_field.value),
                    debt_date=date_field.value,
                    notes=notes_field.value
                )
                self.db.add_teacher_debt(d)
                self.close_dialog(dlg)
                self.load_data(update_ui=True)
                self.show_snackbar(f"Recorded debt for {d.teacher_name}", "#F44336")
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", "#F44336")

        dlg = ft.AlertDialog(
            title=ft.Text("Record Teacher Debt"),
            content=ft.Column([teacher_field, amount_field, date_field, notes_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Save", on_click=add, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    def show_edit_debt_dialog(self, debt):
        """Dialog to edit existing debt record"""
        teacher_field = ft.TextField(label="Teacher Name", value=debt.teacher_name)
        amount_field = ft.TextField(label="Amount Given", value=str(debt.amount), keyboard_type=ft.KeyboardType.NUMBER)
        date_field = ft.TextField(label="Date (YYYY-MM-DD)", value=debt.debt_date)
        notes_field = ft.TextField(label="Notes", value=debt.notes or "", multiline=True, min_lines=2)
        
        def save(e):
            if not teacher_field.value or not amount_field.value: return
            try:
                debt.teacher_name = teacher_field.value
                debt.amount = float(amount_field.value)
                debt.debt_date = date_field.value
                debt.notes = notes_field.value
                self.db.update_teacher_debt(debt)
                self.close_dialog(dlg)
                self.load_data(update_ui=True)
                self.show_snackbar("Record updated", "#2196F3")
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", "#F44336")

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Debt Record"),
            content=ft.Column([teacher_field, amount_field, date_field, notes_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Update", on_click=save, bgcolor="#2196F3", color="white")
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_debt(self, debt):
        """Confirm deletion of debt record"""
        def delete(e):
            self.db.delete_teacher_debt(debt.id)
            self.close_dialog(dlg)
            self.load_data(update_ui=True)
            self.show_snackbar("Record deleted", "#F44336")
            
        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete the debt record for {debt.teacher_name} ({format_currency(debt.amount)})?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    # --- EXPORT ---

    def export_debt_list(self):
        """Export all teacher debt records to Excel"""
        from utils.export import export_teacher_debt_to_excel
        
        try:
            debts = self.db.get_all_teacher_debt()
            if not debts:
                self.show_snackbar("No debt records to export", "#FF9800")
                return
            filename = export_teacher_debt_to_excel(debts)
            self.show_snackbar(f"Exported to {filename}", "#4CAF50")
        except Exception as e:
            self.show_snackbar(f"Export failed: {str(e)}", "#F44336")

    # --- HELPERS ---

    def open_dialog(self, dlg):
        if dlg not in self.main_page.overlay:
            self.main_page.overlay.append(dlg)
        dlg.open = True
        self.main_page.update()

    def close_dialog(self, dlg):
        dlg.open = False
        self.main_page.update()

    def show_snackbar(self, message, color):
        self.main_page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.main_page.snack_bar.open = True
        self.main_page.update()
