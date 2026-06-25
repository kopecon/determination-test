import sys

from Menu.menu import Menu


if __name__ == '__main__':
    # --- Fix for Windows High-DPI Display Scaling ---
    if sys.platform == "win32":
        import ctypes

        try:
            # Tells Windows 8.1 / 10 / 11 to give us true 1:1 screen pixels
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Fallback for older Windows environments
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    # ------------------------------------------------

    Menu().run()