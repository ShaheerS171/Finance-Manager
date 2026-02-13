"""Minimal test to find the correct dialog API for this Flet version."""
import flet as ft

def main(page: ft.Page):
    page.title = "Dialog Test"
    
    # Print available dialog-related methods on Page
    dialog_attrs = [attr for attr in dir(page) if 'dialog' in attr.lower() or 'overlay' in attr.lower() or attr == 'open' or attr == 'close']
    print(f"Dialog-related attrs on Page: {dialog_attrs}")
    print(f"Has page.dialog: {hasattr(page, 'dialog')}")
    print(f"Has page.open: {hasattr(page, 'open')}")
    print(f"Has page.overlay: {hasattr(page, 'overlay')}")
    
    dlg = ft.AlertDialog(
        title=ft.Text("Test Dialog"),
        content=ft.Text("This is a test dialog"),
        actions=[ft.TextButton("Close", on_click=lambda e: close_dlg(e))],
    )
    
    def close_dlg(e):
        dlg.open = False
        page.update()
    
    def open_dialog_method1(e):
        """Try page.dialog = dlg"""
        print("Method 1: page.dialog = dlg")
        try:
            page.dialog = dlg
            dlg.open = True
            page.update()
            print("Method 1 succeeded!")
        except Exception as ex:
            print(f"Method 1 failed: {ex}")
    
    def open_dialog_method2(e):
        """Try page.overlay.append(dlg)"""
        print("Method 2: page.overlay.append(dlg)")
        try:
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()
            print("Method 2 succeeded!")
        except Exception as ex:
            print(f"Method 2 failed: {ex}")
    
    def open_dialog_method3(e):
        """Try page.open(dlg)"""
        print("Method 3: page.open(dlg)")
        try:
            page.open(dlg)
            print("Method 3 succeeded!")
        except Exception as ex:
            print(f"Method 3 failed: {ex}")
    
    page.add(
        ft.Column([
            ft.ElevatedButton("Method 1: page.dialog", on_click=open_dialog_method1),
            ft.ElevatedButton("Method 2: page.overlay", on_click=open_dialog_method2),
            ft.ElevatedButton("Method 3: page.open()", on_click=open_dialog_method3),
        ])
    )

ft.app(main)
