"""
Transport Fee Manager - Main Application
A comprehensive fee management system for transport and events
"""

import flet as ft
from database import DatabaseManager
from ui.home_screen import HomeScreen
from ui.transport_screen import TransportScreen
from ui.events_screen import EventsScreen
from ui.principal_screen import PrincipalScreen
from ui.teacher_debt_screen import TeacherDebtScreen


class TransportFeeManager:
    """Main application class"""
    
    def __init__(self, page: ft.Page):
        print("TransportFeeManager.__init__ started")
        self.page = page
        self.page.title = "Transport Fee Manager"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        # self.page.add(ft.Text("DEBUG: App Started", color="red", size=30))
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Current screen
        self.current_screen = None
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the main user interface"""
        # Theme Toggle
        self.theme_toggle = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED,
            on_click=self.toggle_theme,
            tooltip="Toggle Light/Dark Mode"
        )

        # Navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.DIRECTIONS_BUS_OUTLINED,
                    selected_icon=ft.Icons.DIRECTIONS_BUS,
                    label="Transport",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.EVENT_OUTLINED,
                    selected_icon=ft.Icons.EVENT,
                    label="Events",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                    selected_icon=ft.Icons.ATTACH_MONEY,
                    label="Principal",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINED,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Teachers",
                ),
            ],
            on_change=self.navigate,
            trailing=ft.Container(self.theme_toggle, padding=ft.padding.only(bottom=20))
        )
        
        # Content area
        self.content_area = ft.Container(
            expand=True,
            bgcolor="surfaceVariant",
        )
        
        # Load initial screen
        self.load_screen(0)
        
        # Main layout
        main_layout = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
        
        self.page.add(main_layout)
        print("Main layout added to page")
    
    def navigate(self, e):
        """Handle navigation"""
        selected_index = e.control.selected_index
        self.load_screen(selected_index)
    
    def load_screen(self, index):
        """Load the selected screen"""
        # Clear current content
        self.content_area.content = None
        
        # Load new screen
        if index == 0:
            # Dashboard
            self.current_screen = HomeScreen(self.db, self.page)
        elif index == 1:
            # Transport
            self.current_screen = TransportScreen(self.db, self.page)
        elif index == 2:
            # Events
            self.current_screen = EventsScreen(self.db, self.page)
        elif index == 3:
            # Principal
            self.current_screen = PrincipalScreen(self.db, self.page)
        elif index == 4:
            # Teacher Debt
            self.current_screen = TeacherDebtScreen(self.db, self.page)
        
        # Update content area
        self.content_area.content = self.current_screen
        self.page.update()
        print(f"Loaded screen {index} and updated page")
    
    def refresh_current_screen(self):
        """Refresh the current screen"""
        if hasattr(self.current_screen, 'refresh'):
            self.current_screen.refresh()

    def toggle_theme(self, e):
        """Toggle between light and dark theme"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_toggle.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_toggle.icon = ft.Icons.DARK_MODE_OUTLINED
        
        self.page.update()


def main(page: ft.Page):
    """Main entry point"""
    print("Starting main...")
    TransportFeeManager(page)


if __name__ == "__main__":
    ft.app(target=main)
