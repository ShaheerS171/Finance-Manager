"""
Events Management Screen - Grid & Table View
"""

import flet as ft
from database.models import Event, EventParticipant, EventPayment
from utils.helpers import format_currency, get_current_date, generate_receipt_no

class EventsScreen(ft.Container):
    """Events management screen with Grid and Detail Table"""
    
    def __init__(self, db_manager, page):
        super().__init__()
        self.db = db_manager
        self.main_page = page
        
        self.padding = 20
        self.expand = True
        self.current_event = None
        
        # UI Components
        self.search_term = ""
        self.search_field = ft.TextField(
            label="Search Participant (Name or Phone)",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            width=300,
            text_size=14,
            content_padding=10
        )
        self.events_grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=300,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
        )
        self.participants_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Phone")),
                ft.DataColumn(ft.Text("Due")),
                ft.DataColumn(ft.Text("Paid")),
                ft.DataColumn(ft.Text("Pending")),
                ft.DataColumn(ft.Text("Add Payment")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            vertical_lines=ft.border.BorderSide(1, "#e0e0e0"),
            heading_row_color="#f5f5f5",
        )
        
        self.build_ui()
    
    def build_ui(self):
        """Build UI based on state"""
        self.content = ft.Column()
        if self.current_event is None:
            self.show_events_view()
        else:
            self.show_event_detail_view()

    def show_events_view(self):
        """Show grid of events"""
        self.load_events()
        self.content.controls = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.EVENT, size=32, color="#FF9800"),
                    ft.Text("Events", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Add Event",
                        icon=ft.Icons.ADD,
                        on_click=self.show_add_event_dialog,
                         style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                    )
                ],
            ),
            ft.Divider(),
            ft.Container(content=self.events_grid, expand=True)
        ]

    def show_event_detail_view(self):
        """Show participants table for event"""
        self.load_participants()
        self.content.controls = [
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.navigate_back()),
                    ft.Text(f"Event: {self.current_event.name}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True                    ),
                    ft.VerticalDivider(width=10),
                    ft.ElevatedButton(
                        "Export to Excel",
                        icon=ft.Icons.FILE_DOWNLOAD,
                        on_click=lambda e: self.export_event_details(),
                        style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
                    ),
                    ft.ElevatedButton(
                        "Add Participant",
                        icon=ft.Icons.PERSON_ADD,
                        on_click=self.show_add_participant_dialog,
                        style=ft.ButtonStyle(bgcolor="#2196F3", color="white")
                    )
                ]
            ),
            ft.Divider(),
            # Search Bar
            ft.Row([self.search_field]),
            ft.Divider(),
             ft.Column(
                [self.participants_table],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        ]

    def navigate_back(self):
        self.current_event = None
        self.search_term = ""
        self.search_field.value = ""
        self.build_ui()
        self.update()

    def load_events(self):
        self.events_grid.controls.clear()
        events = self.db.get_all_events()
        
        if not events:
             self.events_grid.controls.append(ft.Text("No events found. Add one!", size=16))
             return

        for event in events:
            progress = event.collected_amount / event.target_amount if event.target_amount > 0 else 0
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.EVENT_NOTE, color="#FF9800"),
                                title=ft.Text(event.name, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"Deadline: {event.deadline or 'N/A'}"),
                            ),
                            ft.ProgressBar(value=progress, color="#4CAF50", bgcolor="#E0E0E0"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Target: {format_currency(event.target_amount)}"),
                                    ft.Text(f"Collected: {format_currency(event.collected_amount)}", color="#4CAF50"),
                                ])
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("Open", on_click=lambda e, ev=event: self.open_event(ev)),
                                    ft.IconButton(ft.Icons.EDIT, icon_color="#2196F3", on_click=lambda e, ev=event: self.show_edit_event_dialog(ev)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="#F44336", on_click=lambda e, ev=event: self.confirm_delete_event(ev)),
                                ],
                                alignment=ft.MainAxisAlignment.END
                            )
                        ],
                        spacing=10
                    ),
                    padding=10
                ),
                elevation=5
            )
            self.events_grid.controls.append(card)

    def open_event(self, event):
        self.current_event = event
        self.search_term = ""
        self.search_field.value = ""
        self.build_ui()
        self.update()

    def on_search_change(self, e):
        """Handle search field changes"""
        self.search_term = e.control.value.lower()
        self.load_participants()
        self.update()

    def load_participants(self):
        self.participants_table.rows.clear()
        if not self.current_event: return
        
        participants = self.db.get_event_participants(self.current_event.id)
        
        # Apply filter
        if self.search_term:
            participants = [
                p for p in participants
                if self.search_term in p.name.lower() or
                   (p.phone and self.search_term in p.phone.lower())
            ]
        
        for p in participants:
            pending = p.amount_due - p.amount_paid
            
            def on_pay_submit(e, participant=p):
                try:
                    amount = float(e.control.value)
                    if amount <= 0: return
                    
                    payment = EventPayment(
                        participant_id=participant.id,
                        amount=amount,
                        payment_date=get_current_date(),
                        receipt_no=generate_receipt_no(),
                        notes="Quick Add"
                    )
                    self.db.add_event_payment(payment)
                    self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Added {format_currency(amount)}"), bgcolor="#4CAF50")
                    self.main_page.snack_bar.open = True
                    self.load_participants()
                    self.main_page.update()
                except ValueError:
                    pass

            self.participants_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.name)),
                        ft.DataCell(ft.Text(p.phone or "-")),
                        ft.DataCell(ft.Text(format_currency(p.amount_due))),
                        ft.DataCell(ft.Text(format_currency(p.amount_paid), color="#4CAF50")),
                        ft.DataCell(ft.Text(format_currency(pending), color="#F44336")),
                        ft.DataCell(
                            ft.TextField(
                                hint_text="Add",
                                width=80,
                                text_size=12,
                                content_padding=5,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_submit=on_pay_submit
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.DELETE, icon_size=16, icon_color="#F44336", on_click=lambda e, pa=p: self.confirm_delete_participant(pa)),
                            ])
                        ),
                    ]
                )
            )

    # --- DIALOGS ---

    def show_add_event_dialog(self, e):
        name_field = ft.TextField(label="Event Name", autofocus=True)
        target_field = ft.TextField(label="Target Amount", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        deadline_field = ft.TextField(label="Deadline (YYYY-MM-DD)", value=get_current_date())
        
        def add(e):
            if not name_field.value: return
            try:
                event = Event(
                    name=name_field.value,
                    target_amount=float(target_field.value),
                    collected_amount=0,
                    deadline=deadline_field.value
                )
                self.db.add_event(event)
                self.close_dialog(dlg)
                self.load_events()
                self.main_page.update()
            except Exception as ex:
                print(ex)

        dlg = ft.AlertDialog(
            title=ft.Text("Add Event"),
            content=ft.Column([name_field, target_field, deadline_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Add", on_click=add)
            ]
        )
        self.open_dialog(dlg)

    def show_edit_event_dialog(self, event):
        name_field = ft.TextField(label="Name", value=event.name)
        target_field = ft.TextField(label="Target", value=str(event.target_amount))
        deadline_field = ft.TextField(label="Deadline", value=event.deadline)

        def save(e):
            event.name = name_field.value
            event.target_amount = float(target_field.value or 0)
            event.deadline = deadline_field.value
            self.db.update_event(event)
            self.close_dialog(dlg)
            self.load_events()
            self.main_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Event"),
            content=ft.Column([name_field, target_field, deadline_field], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Save", on_click=save)
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_event(self, event):
        def delete(e):
            self.db.delete_event(event.id)
            self.close_dialog(dlg)
            self.load_events()
            self.main_page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Delete Event?"),
            content=ft.Text(f"Delete {event.name}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    def show_add_participant_dialog(self, e):
        name_field = ft.TextField(label="Name", autofocus=True)
        phone_field = ft.TextField(label="Phone")
        paid_field = ft.TextField(label="Amount Paid", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        
        def add(e):
            if not name_field.value: return
            try:
                p = EventParticipant(
                    event_id=self.current_event.id,
                    name=name_field.value,
                    phone=phone_field.value,
                    amount_due=self.current_event.target_amount,
                    amount_paid=float(paid_field.value or 0)
                )
                self.db.add_event_participant(p)
                self.close_dialog(dlg)
                self.load_participants()
                self.main_page.update()
            except Exception as ex:
                pass

        dlg = ft.AlertDialog(
            title=ft.Text(f"Add Participant to {self.current_event.name}"),
            content=ft.Column([
                name_field, 
                phone_field, 
                paid_field,
                ft.Text(f"Target: {format_currency(self.current_event.target_amount)}", italic=True, color="#666666", size=12),
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Add", on_click=add)
            ]
        )
        self.open_dialog(dlg)

    def confirm_delete_participant(self, participant):
        def delete(e):
            self.db.delete_event_participant(participant.id)
            self.close_dialog(dlg)
            self.load_participants()
            self.main_page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text("Remove Participant?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dlg)),
                ft.ElevatedButton("Delete", on_click=delete, bgcolor="#F44336", color="white")
            ]
        )
        self.open_dialog(dlg)

    def export_event_details(self):
        """Export current event details and participants to Excel"""
        from utils.export import export_event_to_excel
        if not self.current_event: return
        
        try:
            participants = self.db.get_event_participants(self.current_event.id)
            filename = export_event_to_excel(self.current_event, participants)
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Exported to {filename}"), bgcolor="#4CAF50")
            self.main_page.snack_bar.open = True
            self.main_page.update()
        except Exception as e:
            self.main_page.snack_bar = ft.SnackBar(content=ft.Text(f"Export failed: {str(e)}"), bgcolor="#F44336")
            self.main_page.snack_bar.open = True
            self.main_page.update()

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
