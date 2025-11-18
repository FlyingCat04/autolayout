"""
Garment Line Balancing System - Main Entry Point
==============================================

A desktop application for optimizing garment production line work allocation
based on operation times (SAM) and worker skill levels.
"""

import tkinter as tk
from app.main_window import LineBalancingApp

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = LineBalancingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()