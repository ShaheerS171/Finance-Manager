"""
Reusable UI components
"""

import flet as ft
from utils.helpers import format_currency, calculate_pending, get_payment_status


class StatsCard(ft.Container):
    """Statistics card component"""
    def __init__(self, title, value, subtitle="", color="#2196F3"):
        super().__init__()
        
        self.bgcolor = color
        self.border_radius = 10
        self.padding = 15
        self.expand = True
        
        self.content = ft.Column(
            [
                ft.Text(title, size=14, color="white", weight=ft.FontWeight.W_500),
                ft.Text(value, size=24, color="white", weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=12, color="white70") if subtitle else ft.Container(),
            ],
            spacing=5,
        )


class StudentCard(ft.Container):
    """Student information card"""
    def __init__(self, student, on_click=None, on_pay=None, on_edit=None, on_delete=None):
        super().__init__()
        
        pending = calculate_pending(student.target_amount, student.paid_amount)
        status = get_payment_status(student.target_amount, student.paid_amount)
        
        # Status color
        status_color = {
            "Paid": "#4CAF50",
            "Partial": "#FF9800",
            "Pending": "#F44336"
        }.get(status, "#757575")
        
        self.bgcolor = ft.Colors.SURFACE_VARIANT
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)
        
        # Action buttons
        actions = []
        if on_pay:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.PAYMENT,
                    icon_color="#4CAF50",
                    tooltip="Add Payment",
                    on_click=lambda e: on_pay(student)
                )
            )
        if on_edit:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color="#2196F3",
                    tooltip="Edit",
                    on_click=lambda e: on_edit(student)
                )
            )
        if on_delete:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="#F44336",
                    tooltip="Delete",
                    on_click=lambda e: on_delete(student)
                )
            )
        
        self.content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(student.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(status, size=12, color="white"),
                                        bgcolor=status_color,
                                        padding=5,
                                        border_radius=5,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Class: {student.class_name}", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(f"Phone: {student.phone or 'N/A'}", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Target", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(student.target_amount), size=14, weight=ft.FontWeight.BOLD),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Paid", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(student.paid_amount), size=14, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Pending", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(pending), size=14, weight=ft.FontWeight.BOLD, color="#F44336"),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                        ],
                        spacing=5,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(actions, spacing=5),
                    alignment=ft.Alignment(1.0, 0.0),
                ) if actions else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        if on_click:
            self.on_click = lambda e: on_click(student)
            self.ink = True


class EventCard(ft.Container):
    """Event information card"""
    def __init__(self, event, on_click=None, on_edit=None, on_delete=None):
        super().__init__()
        
        pending = calculate_pending(event.target_amount, event.collected_amount)
        progress = (event.collected_amount / event.target_amount * 100) if event.target_amount > 0 else 0
        
        self.bgcolor = ft.Colors.SURFACE_VARIANT
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)
        
        # Action buttons
        actions = []
        if on_edit:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color="#2196F3",
                    tooltip="Edit",
                    on_click=lambda e: on_edit(event)
                )
            )
        if on_delete:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="#F44336",
                    tooltip="Delete",
                    on_click=lambda e: on_delete(event)
                )
            )
        
        self.content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(event.name, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(event.description or "", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(f"Deadline: {event.deadline or 'No deadline'}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Target", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(event.target_amount), size=14, weight=ft.FontWeight.BOLD),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Collected", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(event.collected_amount), size=14, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Pending", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(pending), size=14, weight=ft.FontWeight.BOLD, color="#F44336"),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                            ft.ProgressBar(value=progress / 100, color="#4CAF50", bgcolor="#E0E0E0", height=8),
                            ft.Text(f"{progress:.1f}% Complete", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ],
                        spacing=5,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(actions, spacing=5),
                    alignment=ft.Alignment(1.0, 0.0),
                ) if actions else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        if on_click:
            self.on_click = lambda e: on_click(event)
            self.ink = True


class ParticipantCard(ft.Container):
    """Event participant card"""
    def __init__(self, participant, on_pay=None, on_edit=None, on_delete=None):
        super().__init__()
        
        pending = calculate_pending(participant.amount_due, participant.amount_paid)
        status = get_payment_status(participant.amount_due, participant.amount_paid)
        
        # Status color
        status_color = {
            "Paid": "#4CAF50",
            "Partial": "#FF9800",
            "Pending": "#F44336"
        }.get(status, "#757575")
        
        self.bgcolor = ft.Colors.SURFACE_VARIANT
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)
        
        # Action buttons
        actions = []
        if on_pay:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.PAYMENT,
                    icon_color="#4CAF50",
                    tooltip="Add Payment",
                    on_click=lambda e: on_pay(participant)
                )
            )
        if on_edit:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color="#2196F3",
                    tooltip="Edit",
                    on_click=lambda e: on_edit(participant)
                )
            )
        if on_delete:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="#F44336",
                    tooltip="Delete",
                    on_click=lambda e: on_delete(participant)
                )
            )
        
        self.content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(participant.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(status, size=12, color="white"),
                                        bgcolor=status_color,
                                        padding=5,
                                        border_radius=5,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Phone: {participant.phone or 'N/A'}", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Due", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(participant.amount_due), size=14, weight=ft.FontWeight.BOLD),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Paid", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(participant.amount_paid), size=14, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Pending", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text(format_currency(pending), size=14, weight=ft.FontWeight.BOLD, color="#F44336"),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                        ],
                        spacing=5,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(actions, spacing=5),
                    alignment=ft.Alignment(1.0, 0.0),
                ) if actions else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


class SearchBar(ft.TextField):
    """Search bar component"""
    def __init__(self, hint_text="Search...", on_change=None):
        super().__init__(
            hint_text=hint_text,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            filled=True,
            expand=True,
            on_change=on_change,
        )
