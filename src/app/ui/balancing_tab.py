"""
Balancing Tab UI Module
=======================

This module contains the UI components for the line balancing tab.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class BalancingTab:
    """Balancing tab UI component"""
    
    def __init__(self, parent, main_app, bg_color):
        self.parent = parent
        self.main_app = main_app
        self.bg_color = bg_color
        self.sort_column = 'operation_sequence'
        self.sort_order = 'asc'
        
        # Create the frame for this tab
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the balancing tab UI"""
        # Frame điều khiển với hiệu ứng card
        control_frame = ttk.LabelFrame(self.frame, text="Điều Khiển", padding=15, style='Card.TLabelframe')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Thêm frame cho các tham số tính toán takt time
        takt_frame = ttk.LabelFrame(control_frame, text="Thông Số Takt Time", padding=10)
        takt_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(takt_frame, text="Thời gian làm việc (phút):").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.working_time = ttk.Entry(takt_frame, width=10)
        self.working_time.insert(0, "480")  # 8 giờ = 480 phút
        self.working_time.grid(row=0, column=1, padx=(0, 10))
        
        self.takt_time_label = ttk.Label(takt_frame, text="Takt Time: -- giây", font=('Arial', 9, 'bold'))
        self.takt_time_label.grid(row=0, column=2, padx=(20, 0))
        
        # Nút thực hiện với style modern
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="⚖️ Cân Bằng Chuyền", 
                  command=self.main_app.balance_line, 
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="📊 Export Kết Quả", 
                  command=self.main_app.export_results, 
                  style='TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="📈 Hiển Thị Thống Kê", 
                  command=self.main_app.show_statistics, 
                  style='TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Làm Mới", 
                  command=self.main_app.reset_data, 
                  style='Danger.TButton').pack(side='left', padx=5)
        
        # Frame kết quả với hiệu ứng card
        result_frame = ttk.LabelFrame(self.frame, text="Phân Công Công Việc", padding=10, style='Card.TLabelframe')
        result_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Tạo treeview với scrollbar cho kết quả
        tree_container = tk.Frame(result_frame, bg='white')
        tree_container.pack(fill='both', expand=True)
        
        # Bảng phân công
        self.result_tree = ttk.Treeview(tree_container, 
                                        columns=('worker', 'operation', 'sam', 'efficiency', 'time'),
                                        show='headings', height=8)
        # Configure column headings with sorting
        columns = [
            ('worker', 'Công Nhân'),
            ('operation', 'Công Đoạn'),
            ('sam', 'SAM (s)'),
            ('efficiency', 'Hiệu Suất (%)'),
            ('time', 'Thời Gian Thực Tế (s)')
        ]
        
        for col_id, col_text in columns:
            self.result_tree.heading(col_id, text=col_text, 
                                   command=lambda c=col_id: self.sort_by_column(c))
        
        self.result_tree.column('worker', width=150)
        self.result_tree.column('operation', width=250)
        self.result_tree.column('sam', width=100)
        self.result_tree.column('efficiency', width=120)
        self.result_tree.column('time', width=120)
        
        
        # Thêm sự kiện double-click để xem chi tiết
        self.result_tree.bind("<Double-1>", self.on_assignment_double_click)
        
        # Tạo thanh cuộn dọc và ngang
        scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.result_tree.yview)
        scrollbar_x = ttk.Scrollbar(result_frame, orient='horizontal', command=self.result_tree.xview)  # Di chuyển xuống dưới
        self.result_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Bố trí các thành phần
        self.result_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')  # Đặt ở dưới cùng
    
    def on_assignment_double_click(self, event):
        """Handle double-click on assignment row"""
        item = self.result_tree.selection()
        if not item:
            return
            
        # Get selected item values
        values = self.result_tree.item(item, 'values')
        if not values:
            return
            
        # Show assignment details
        worker, operation, sam, efficiency, time = values
        
        detail_window = tk.Toplevel(self.main_app.root)
        detail_window.title("Chi Tiết Phân Công")
        detail_window.geometry("400x250")
        detail_window.configure(bg='white')
        detail_window.resizable(False, False)
        
        # Center the window
        detail_window.transient(self.main_app.root)
        detail_window.grab_set()
        
        # Create a main frame with padding
        main_frame = tk.Frame(detail_window, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Chi Tiết Phân Công", 
                              font=('Arial', 14, 'bold'), bg='white', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Details grid
        details_frame = tk.Frame(main_frame, bg='white')
        details_frame.pack(fill='both', expand=True)
        
        # Display details
        details = [
            ("Công nhân", worker),
            ("Công đoạn", operation),
            ("SAM", f"{sam} giây"),
            ("Hiệu suất", f"{efficiency}%"),
            ("Thời gian thực tế", f"{time} giây")
        ]
        
        for label, value in details:
            row_frame = tk.Frame(main_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            label_label = tk.Label(row_frame, text=label, width=20, anchor='w', bg='white', font=('Arial', 9, 'bold'))
            label_label.pack(side='left')
            
            value_label = tk.Label(row_frame, text=value, anchor='w', bg='white')
            value_label.pack(side='left', fill='x', expand=True)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Đóng", command=detail_window.destroy, style='Accent.TButton')
        close_btn.pack(pady=(20, 0))
        
        # Center window on parent
        detail_window.update_idletasks()
        x = self.main_app.root.winfo_x() + (self.main_app.root.winfo_width() // 2) - (detail_window.winfo_width() // 2)
        y = self.main_app.root.winfo_y() + (self.main_app.root.winfo_height() // 2) - (detail_window.winfo_height() // 2)
        detail_window.geometry(f"+{x}+{y}")
    
    def refresh_results_table(self):
        """Refresh the results table display"""
        # Clear all items
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Display results (already sorted)
        for result in self.main_app.balancing_results:
            self.result_tree.insert('', 'end', values=(
                result['worker'],
                result['operation'],
                f"{result['sam']:.2f}",
                f"{result['efficiency']:.0f}",
                f"{result['time']:.2f}"
            ))
        
        # Update column headers to show sort indicator
        columns = [
            ('worker', 'Công Nhân'),
            ('operation', 'Công Đoạn'),
            ('sam', 'SAM (s)'),
            ('efficiency', 'Hiệu Suất (%)'),
            ('time', 'Thời Gian Thực Tế (s)')
        ]
        
        for col_id, col_text in columns:
            sort_indicator = ''
            if col_id == self.sort_column:
                sort_indicator = ' 🔼' if self.sort_order == 'asc' else ' 🔽'
            self.result_tree.heading(col_id, text=f"{col_text}{sort_indicator}")
    
    def sort_by_column(self, col):
        """Sort results by column"""
        # Toggle sort order if clicking the same column
        if self.sort_column == col:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.sort_column = col
            self.sort_order = 'asc'
        
        if hasattr(self.main_app, 'balancing_results'):
            self.apply_sorting()
            self.refresh_results_table()
    
    def apply_sorting(self):
        """Apply sorting to results data"""
        if not hasattr(self.main_app, 'balancing_results'):
            return
            
        col = self.sort_column
        order = self.sort_order
        
        # Tạo mapping từ tên công đoạn sang sequence để sắp xếp
        op_sequence_map = {}
        for op in self.main_app.operations:
            op_sequence_map[op['name']] = op.get('sequence', 0)
        
        # Define sort key function
        def sort_key(result):
            if col == 'operation_sequence':
                # Sắp xếp theo sequence của công đoạn
                return op_sequence_map.get(result.get('operation', ''), 0)
            elif col in ['sam', 'efficiency', 'time']:
                # Numeric sort
                try:
                    return float(result.get(col, 0))
                except:
                    return 0
            else:
                # String sort
                return str(result.get(col, '')).lower()
        
        # Sort results
        reverse = (order == 'desc')
        self.main_app.balancing_results.sort(key=sort_key, reverse=reverse)
    
    def refresh_results(self):
        """Clear all results from the treeview and reset UI elements"""
        try:
            # Clear previous results
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # Reset takt time label
            self.takt_time_label.config(text="Takt Time: -- giây")
            
            # Reset working time entry to default
            self.working_time.delete(0, tk.END)
            self.working_time.insert(0, "480")  # 8 hours = 480 minutes
            
        except Exception as e:
            # In case of any error, show a warning but don't stop the application
            print(f"Warning: Could not fully refresh results: {str(e)}")
    
    def calculate_takt_time(self):
        """Calculate and display takt time based on working time, total SAM and number of workers"""
        try:
            working_time = float(self.working_time.get()) * 60  # Convert to seconds
            total_sam = self.main_app.calculate_total_sam()
            num_workers = len(self.main_app.workers)
            
            # Kiểm tra điều kiện trước khi tính toán
            if num_workers <= 0:
                messagebox.showwarning("Cảnh báo", "Vui lòng thêm công nhân trước!")
                return
                
            if total_sam <= 0:
                messagebox.showwarning("Cảnh báo", "Vui lòng thêm công đoạn trước!")
                return
            
            # Tính takt time và sản lượng mục tiêu
            # Takt time = Tổng SAM / Số công nhân (để đảm bảo sử dụng hết công nhân)
            optimal_takt_time = total_sam / num_workers
            # Sản lượng mục tiêu = Thời gian làm việc / Takt time
            target_production = working_time / optimal_takt_time
            
            self.takt_time_label.config(
                text=f"Takt Time: {optimal_takt_time:.2f} giây (Sản lượng: {target_production:.0f} sản phẩm)"
            )
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Giá trị không hợp lệ: {str(e)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi không xác định: {str(e)}")