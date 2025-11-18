"""
Main Window Module for Garment Line Balancing System
===================================================

This module contains the main application window class that orchestrates
all the UI components and core functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import List, Dict, Tuple
import json

from .ui.operations_tab import OperationsTab
from .ui.workers_tab import WorkersTab
from .ui.balancing_tab import BalancingTab
from .ui.charts_tab import ChartsTab
from .core.data_manager import DataManager
from .core.line_balancer import LineBalancer


class LineBalancingApp:
    """Main application window class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Cân Bằng Chuyền May")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configure modern styles
        self.setup_styles()
        
        # Data storage
        self.operations = []  # [{code, name, sam, machine}]
        self.workers = []     # [{name, skills: {machine_type: score}}]
        self.assignments = [] # Line balancing results
        self.balancing_results = [] # Store results data for sorting
        self.efficiency_stats = {} # Efficiency statistics
        
        # Core components
        self.data_manager = DataManager(self)
        self.line_balancer = LineBalancer(self)
        
        self.setup_ui()
    
    def setup_styles(self):
        """Setup modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#f8f9fa'
        self.accent_color = '#4a7abc'
        self.success_color = '#28a745'
        self.warning_color = '#ffc107'
        self.danger_color = '#dc3545'
        
        # Modern button styles
        style.configure('Accent.TButton', 
                       foreground='white', 
                       background=self.accent_color,
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none',
                       padding=(10, 5))
        style.map('Accent.TButton', 
                 background=[('active', '#3a6aac')])
        
        style.configure('Success.TButton', 
                       foreground='white', 
                       background=self.success_color,
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none',
                       padding=(10, 5))
        style.map('Success.TButton', 
                 background=[('active', '#218838')])
        
        style.configure('Danger.TButton', 
                       foreground='white', 
                       background=self.danger_color,
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none',
                       padding=(10, 5))
        style.map('Danger.TButton', 
                 background=[('active', '#c82333')])
        
        # Modern frame styles
        style.configure('Card.TLabelframe', 
                       background='white',
                       borderwidth=1,
                       relief='solid')
        style.configure('Card.TLabelframe.Label', 
                       background='white',
                       foreground='#333333',
                       font=('Arial', 10, 'bold'))
        
        # Modern notebook styles
        style.configure('TNotebook', 
                       background=self.bg_color,
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#e9ecef',
                       foreground='#495057',
                       padding=(15, 5),
                       font=('Arial', 9))
        style.map('TNotebook.Tab', 
                 background=[('selected', 'white')],
                 foreground=[('selected', '#212529')])
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Create a main container with subtle gradient effect
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main notebook with modern effect
        self.notebook = ttk.Notebook(self.main_container, style='TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.operations_tab = OperationsTab(self.notebook, self, bg_color=self.bg_color)
        self.notebook.add(self.operations_tab.frame, text='  Công Đoạn  ')
        
        self.workers_tab = WorkersTab(self.notebook, self, bg_color=self.bg_color)
        self.notebook.add(self.workers_tab.frame, text='  Công Nhân  ')
        
        self.balancing_tab = BalancingTab(self.notebook, self, bg_color=self.bg_color)
        self.notebook.add(self.balancing_tab.frame, text='  Cân Bằng Chuyền  ')
        
        # Tạo tab mới cho biểu đồ
        self.charts_tab = ChartsTab(self.notebook, self, bg_color=self.bg_color)
        self.notebook.add(self.charts_tab.frame, text='  Biểu Đồ  ')

    
    # Data management methods
    def import_operations(self):
        """Import operations from Excel file"""
        return self.data_manager.import_operations()
    
    def export_operations(self):
        """Export operations to Excel file"""
        return self.data_manager.export_operations()
    
    def import_workers(self):
        """Import workers from Excel file"""
        return self.data_manager.import_workers()
    
    def export_workers(self):
        """Export workers to Excel file"""
        return self.data_manager.export_workers()
    
    # Line balancing methods
    def balance_line(self):
        """Balance the production line"""
        return self.line_balancer.balance_line()
    
    def calculate_efficiency_stats(self, worker_loads, worker_assignments):
        """Calculate efficiency statistics"""
        return self.line_balancer.calculate_efficiency_stats(worker_loads, worker_assignments)
    
    def display_results(self):
        """Display balancing results"""
        # Directly call the line balancer's display method
        self.line_balancer.display_results()
    
    # def plot_charts(self):  # Đã chuyển biểu đồ sang tab riêng nên bỏ phương thức này
    #     """Plot charts for visualization"""
    #     return self.line_balancer.plot_charts()
    
    # Utility methods
    def calculate_total_sam(self):
        """Calculate total SAM of all operations"""
        return sum(op['sam'] for op in self.operations)
    
    def refresh_operations_table(self):
        """Refresh operations table display"""
        self.operations_tab.refresh_table()
    
    def refresh_workers_table(self):
        """Refresh workers table display"""
        self.workers_tab.refresh_table()
    
    def export_results(self):
        """Export balancing results"""
        return self.data_manager.export_results()
    
    def show_statistics(self):
        """Show statistics dialog"""
        # Kiểm tra dữ liệu trước khi hiển thị
        if not self.operations:
            messagebox.showwarning("Cảnh báo", "Chưa có công đoạn nào!")
            return
            
        if not self.workers:
            messagebox.showwarning("Cảnh báo", "Chưa có công nhân nào!")
            return
        
        # Nếu chưa có dữ liệu thống kê, yêu cầu cân bằng chuyền trước
        if not self.assignments:
            messagebox.showwarning("Cảnh báo", "Vui lòng cân bằng chuyền trước khi xem thống kê!")
            return
            
        if not self.efficiency_stats:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu thống kê! Hãy cân bằng chuyền trước.")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Thống Kê Hiệu Suất")
        stats_window.geometry("500x450")
        stats_window.configure(bg='white')
        stats_window.resizable(False, False)
        
        # Center the window
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Create a main frame with padding
        main_frame = tk.Frame(stats_window, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Thống Kê Hiệu Suất Cân Bằng", 
                              font=('Arial', 14, 'bold'), bg='white', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Statistics grid
        stats_frame = tk.Frame(main_frame, bg='white')
        stats_frame.pack(fill='both', expand=True)
        
        # Display statistics
        stats = [
            ("Tổng số công đoạn", self.efficiency_stats['total_operations']),
            ("Tổng số công nhân", self.efficiency_stats['total_workers']),
            ("Tổng SAM", f"{self.line_balancer.calculate_total_sam():.2f} giây"),
            ("Tải cao nhất", f"{self.efficiency_stats['max_workload']:.2f} giây"),
            ("Tải thấp nhất", f"{self.efficiency_stats['min_workload']:.2f} giây"),
            ("Tải trung bình", f"{self.efficiency_stats['avg_workload']:.2f} giây"),
            ("Độ lệch chuẩn", f"{self.efficiency_stats['std_deviation']:.2f}"),
            ("Hiệu suất cân bằng", f"{self.efficiency_stats['balance_efficiency']:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats):
            row_frame = tk.Frame(stats_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            label_label = tk.Label(row_frame, text=label, width=25, anchor='w', bg='white')
            label_label.pack(side='left')
            
            value_label = tk.Label(row_frame, text=value, anchor='w', bg='white', font=('Arial', 9, 'bold'))
            value_label.pack(side='left', fill='x', expand=True)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Đóng", command=stats_window.destroy, style='Accent.TButton')
        close_btn.pack(pady=(20, 0))
        
        # Center window on parent
        stats_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (stats_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (stats_window.winfo_height() // 2)
        stats_window.geometry(f"+{x}+{y}")
    
    def reset_data(self):
        """Reset all data to start a new session"""
        # Confirm with user before resetting
        result = messagebox.askyesno(
            "Xác nhận làm mới", 
            "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu và bắt đầu phiên làm việc mới không?\n\n"
            "Thao tác này sẽ:\n"
            "- Xóa tất cả công đoạn\n"
            "- Xóa tất cả công nhân\n"
            "- Xóa kết quả cân bằng\n"
            "- Đặt lại tất cả giao diện về trạng thái ban đầu"
        )
        if not result:
            return
        
        try:
            # Clear all data
            self.operations.clear()
            self.workers.clear()
            self.assignments.clear()
            self.balancing_results.clear()
            self.efficiency_stats.clear()
            
            # Refresh all UI components
            self.operations_tab.refresh_table()
            self.workers_tab.refresh_table()
            self.balancing_tab.refresh_results()
            
            # Reset takt time label
            self.balancing_tab.takt_time_label.config(text="Takt Time: -- giây")
            
            # Refresh charts if the tab exists
            if hasattr(self, 'charts_tab'):
                self.charts_tab.refresh_charts()
            
            messagebox.showinfo("Làm mới thành công", "Đã xóa toàn bộ dữ liệu. Bạn có thể bắt đầu phiên làm việc mới.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể làm mới dữ liệu: {str(e)}")
