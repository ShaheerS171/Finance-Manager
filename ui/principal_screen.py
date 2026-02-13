"""
Principal Payments Tracking Screen
- Excel-like table for viewing/editing/deleting payments
- Totals card for summary
"""

import flet as ft
from database.models import PrincipalPayment
from utils.helpers import format_currency, get_current_date

class PrincipalScreen(ft.Container):
    """Screen for tracking payments made to the Principal/Owner"""
    
    def __init__(self, db_manager, page):
        super().__init__()
        self.db = db_manager
        self.main_page = page
        
        self.padding = 20
        self.expand = True
        
        # UI Components
        self.total_amount_text = ft.Text("PKR 0", size=32, weight=ft.FontWeight.BOLD, color="#4CAF50")
        self.payment_count_text = ft.Text("0 payments recorded", size=14, color="#666666")
        
        self.total_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total Paid to Principal", size=16, weight=ft.FontWeight.BOLD),
                    self.total_amount_text,
                    self.payment_count_text,
                ]),
                padding=20,
            ),
            elevation=5
        )
        
        self.payments_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Amount"), numeric=True),
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
                ft.Icon(ft.Icons.ATTACH_MONEY, size=32, color="#4CAF50"),
                ft.Text("Principal Payments", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add Payment",
                    icon=ft.Icons.ADD,
                    on_click=self.show_add_payment_dialog,
                    style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            # Stats Card
            ft.Row([self.total_card], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(),
            
            # Table Container (Scrollable)
            ft.Text("Payment History", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([self.payments_table], scroll=ft.ScrollMode.AUTO),
                expand=True,
                border=ft.border.all(1, "#EEEEEE"),
                border_radius=10,
                padding=10,
                bgcolor="white"
            )
        ])

    def load_data(self, update_ui=False):
        """Load payments and update summary"""
        # Load summary
        stats = self.db.get_principal_stats()
        self.total_amount_text.value = format_currency(stats['total_paid'])
        self.payment_count_text.value = f"{stats['payment_count']} payments recorded"
        
        # Load table
        self.payments_table.rows.clear()
        payments = self.db.get_all_principal_payments()
        
        for p in payments:
            self.payments_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.payment_date)),
                        ft.DataCell(ft.Text(format_currency(p.amount), weight=ft.FontWeight.BOLD, color="#4CAF50")),
                        ft.DataCell(ft.Text(p.notes or "-")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, icon_color="#2196F3", on_click=lambda e, pay=p: self.show_edit_payment_dialog(pay)),
                                ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="#F44336", on_click=lambda e, pay=p: self.confirm_delete_payment(pay)),
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

    def show_add_payment_dialog(self, e):
        """Dialog to add principal payment"""
        amount_field = ft.TextField(label="Amount Paid", autofocus=True, keyboard_type=ft.KeyboardType.NUMBER)
        date_field = ft.TextField(label="Payment Date (YYYY-MM-DD)", value=get_current_date())
        notes_field = ft.TextField(label="Notes (Optional)", multiline=True, min_lines=2)
        
        def add(e):
            if not amount_field.value: return
            try:
                p = PrincipalPayment(
                    amount=float(amount_field.value),
                    payment_date=date_field.value,
                    notes=notes_field.value
                )
                self.db.add_principal_payment(p)
                self.close_dialog(dlg)
                self.load_data(update_ui=True)
                self.show_snackbar(f"Added payment: {format_currency(p.amount)}", "#4CAF50")
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", "#F44336")

        dlg = ft.AlertDialog(
            title=ft.Text("Record Payment to Principal"),
            content=ft.Column([amount_field, date_field, notes_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Save", on_click=add, bgcolor="#4CAF50", color="white")
            ]
        )
        self.open_dialog(dlg)

    def show_edit_payment_dialog(self, payment):
        """Dialog to edit existing payment"""
        amount_field = ft.TextField(label="Amount Paid", value=str(payment.amount), keyboard_type=ft.KeyboardType.NUMBER)
        date_field = ft.TextField(label="Payment Date (YYYY-MM-DD)", value=payment.payment_date)
        notes_field = ft.TextField(label="Notes", value=payment.notes or "", multiline=True, min_lines=2)
        
        def save(e):
            if not amount_field.value: return
            try:
                payment.amount = float(amount_field.value)
                payment.payment_date = date_field.value
                payment.notes = notes_field.value
                self.db.update_principal_payment(payment)
                self.close_dialog(dlg)
                self.load_data(update_ui=True)
                self.show_snackbar("Payment updated successfully", "#2196F3")
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", "#F44336")

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Payment Record"),
            content=ft.Column([amount_field, date_field, notes_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Update", on_click=save, bgcolor="#2196F3", color="white")
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_payment(self, payment):
        """Confirm deletion of payment record"""
        def delete(e):
            self.db.delete_principal_payment(payment.id)
            self.close_dialog(dlg)
            self.load_data(update_ui=True)
            self.show_snackbar("Payment record deleted", "#F44336")
            
        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete the payment of {format_currency(payment.amount)} on {payment.payment_date}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

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
