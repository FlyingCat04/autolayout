"""
Operations Tab UI Module
========================

This module contains the UI components for the operations management tab.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class OperationsTab:
    """Operations tab UI component"""
    
    def __init__(self, parent, main_app, bg_color):
        self.parent = parent
        self.main_app = main_app
        self.bg_color = bg_color
        self.sort_column = 'sequence'
        self.sort_order = 'asc'
        
        # Create the frame for this tab
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the operations tab UI"""
        # Frame nhập liệu với hiệu ứng card
        input_frame = ttk.LabelFrame(self.frame, text="Nhập Công Đoạn", padding=15, style='Card.TLabelframe')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Tạo frame cho cột bên trái và bên phải
        left_frame = tk.Frame(input_frame, bg='white')
        left_frame.grid(row=0, column=0, sticky='nw', padx=(0, 20))
        
        right_frame = tk.Frame(input_frame, bg='white')
        right_frame.grid(row=0, column=1, sticky='nw')
        
        # Cột bên trái: Số thứ tự, Tên công đoạn, SAM
        ttk.Label(left_frame, text="Số thứ tự:").grid(row=0, column=0, sticky='w', pady=5)
        self.op_sequence = ttk.Entry(left_frame, width=20)
        self.op_sequence.grid(row=0, column=1, sticky='w', pady=5, padx=(5, 0))
        
        ttk.Label(left_frame, text="Tên công đoạn:").grid(row=1, column=0, sticky='w', pady=5)
        self.op_name = ttk.Entry(left_frame, width=30)
        self.op_name.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(left_frame, text="SAM (giây):").grid(row=2, column=0, sticky='w', pady=5)
        self.op_sam = ttk.Entry(left_frame, width=20)
        self.op_sam.grid(row=2, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Cột bên phải: Mã công đoạn, Loại máy, Độ khó
        ttk.Label(right_frame, text="Mã công đoạn:").grid(row=0, column=0, sticky='w', pady=5)
        self.op_code = ttk.Entry(right_frame, width=20)
        self.op_code.grid(row=0, column=1, sticky='w', pady=5, padx=(5, 0))
        
        ttk.Label(right_frame, text="Loại máy:").grid(row=1, column=0, sticky='w', pady=5)
        self.op_machine = ttk.Combobox(right_frame, width=28, values=[
            "Máy 1 kim",
            "Máy 2 kim",
            "Máy vắt sổ",
            "Máy viền/Máy đánh bông",
            "Máy chuyên dụng",
            "Phụ/Ủi"
        ])
        self.op_machine.grid(row=1, column=1, sticky='w', pady=5, padx=(5, 0))
        
        ttk.Label(right_frame, text="Độ khó:").grid(row=2, column=0, sticky='w', pady=5)
        self.op_difficulty = ttk.Combobox(right_frame, width=28, values=[
            "Dễ",
            "Trung bình",
            "Cao"
        ])
        self.op_difficulty.grid(row=2, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Frame chứa các nút chức năng
        btn_frame = tk.Frame(input_frame, bg='white')
        btn_frame.grid(row=0, column=2, rowspan=3, sticky='ns', padx=(20, 0))
        
        # Các nút chức năng
        ttk.Button(btn_frame, text="Thêm Công Đoạn", command=self.add_operation, style='Accent.TButton').pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="Import Excel", command=self.main_app.import_operations, style='TButton').pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="Export Excel", command=self.main_app.export_operations, style='TButton').pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="Xóa Công Đoạn", command=self.delete_operation, style='Danger.TButton').pack(fill='x', pady=2)
        
        # Cấu hình grid
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=0)  # Cột nút không mở rộng
        
        # Bảng hiển thị với hiệu ứng card
        table_frame = ttk.LabelFrame(self.frame, text="Danh Sách Công Đoạn", padding=10, style='Card.TLabelframe')
        table_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Tạo treeview với scrollbar
        tree_container = tk.Frame(table_frame, bg='white')
        tree_container.pack(fill='both', expand=True)
        
        self.ops_tree = ttk.Treeview(tree_container, columns=('sequence', 'code', 'name', 'sam', 'machine', 'difficulty', 'assigned_1', 'assigned_2', 'assigned_3', 'assigned_4'), 
                                      show='headings', height=12)
        self.ops_tree.heading('sequence', text='Thứ Tự', command=lambda: self.sort_by_column('sequence'))
        self.ops_tree.heading('code', text='Mã', command=lambda: self.sort_by_column('code'))
        self.ops_tree.heading('name', text='Tên Công Đoạn', command=lambda: self.sort_by_column('name'))
        self.ops_tree.heading('sam', text='SAM (s)', command=lambda: self.sort_by_column('sam'))
        self.ops_tree.heading('machine', text='Loại Máy', command=lambda: self.sort_by_column('machine'))
        self.ops_tree.heading('difficulty', text='Độ Khó', command=lambda: self.sort_by_column('difficulty'))
        self.ops_tree.heading('assigned_1', text='CN Chỉ Định 1', command=lambda: self.sort_by_column('assigned_1'))
        self.ops_tree.heading('assigned_2', text='CN Chỉ Định 2', command=lambda: self.sort_by_column('assigned_2'))
        self.ops_tree.heading('assigned_3', text='CN Chỉ Định 3', command=lambda: self.sort_by_column('assigned_3'))
        self.ops_tree.heading('assigned_4', text='CN Chỉ Định 4', command=lambda: self.sort_by_column('assigned_4'))
        
        self.ops_tree.column('sequence', width=80)
        self.ops_tree.column('code', width=100)
        self.ops_tree.column('name', width=250)
        self.ops_tree.column('sam', width=100)
        self.ops_tree.column('machine', width=150)
        self.ops_tree.column('difficulty', width=100)
        self.ops_tree.column('assigned_1', width=120)
        self.ops_tree.column('assigned_2', width=120)
        self.ops_tree.column('assigned_3', width=120)
        self.ops_tree.column('assigned_4', width=120)
        
        # Add sorting functionality to column headers
        for col in ['sequence', 'code', 'name', 'sam', 'machine', 'difficulty', 'assigned_1', 'assigned_2', 'assigned_3', 'assigned_4']:
            self.ops_tree.heading(col, command=lambda c=col: self.sort_by_column(c))
        
        # Style for treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        
        # Thêm sự kiện click để chỉnh sửa trực tiếp
        self.ops_tree.bind("<Double-1>", self.on_item_double_click)
        self.ops_tree.bind("<Button-1>", self.on_item_click)
        
        # Tạo thanh cuộn dọc và ngang
        scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.ops_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal', command=self.ops_tree.xview)  # Di chuyển xuống dưới
        self.ops_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Bố trí các thành phần
        self.ops_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')  # Đặt ở dưới cùng
        
        # Load initial data
        self.refresh_table()
    
    def on_item_click(self, event):
        """Handle single click on treeview items"""
        # Get the clicked region
        region = self.ops_tree.identify("region", event.x, event.y)
        column = self.ops_tree.identify_column(event.x)  # Sửa lỗi: chỉ cần truyền event.x
        row = self.ops_tree.identify_row(event.y)
        
        # Only handle cell clicks (not headings)
        if region == "cell" and row:
            # Get column name
            col_id = int(column[1:]) - 1  # Convert to 0-based index
            col_names = ['sequence', 'code', 'name', 'sam', 'machine', 'difficulty', 'assigned_1', 'assigned_2', 'assigned_3', 'assigned_4']
            if 0 <= col_id < len(col_names):
                col_name = col_names[col_id]
                
                # Allow editing for specific columns
                if col_name in ['machine', 'difficulty']:
                    self.show_dropdown_editor(event, row, col_name)
                elif col_name in ['sequence', 'sam']:  # Allow direct editing for sequence and SAM
                    self.show_entry_editor(event, row, col_name)
                elif col_name in ['assigned_1', 'assigned_2', 'assigned_3', 'assigned_4']:
                    self.show_worker_assignment_editor(event, row, col_name)
    
    def show_entry_editor(self, event, item, column):
        """Show entry editor for specific columns"""
        # Get current value
        values = self.ops_tree.item(item, 'values')
        col_names = ['sequence', 'code', 'name', 'sam', 'machine', 'difficulty']
        col_index = col_names.index(column)
        current_value = values[col_index]
        
        # Create an entry at the cell position
        bbox = self.ops_tree.bbox(item, column)
        if bbox:  # Check if bbox is valid
            x, y, width, height = bbox
            popup = tk.Toplevel(self.ops_tree)
            popup.overrideredirect(True)
            popup.configure(bg='#f0f0f0')  # Light gray background
            
            # Position the popup
            popup_x = x + self.ops_tree.winfo_rootx()
            popup_y = y + self.ops_tree.winfo_rooty()
            popup.geometry(f"{width}x{height}+{popup_x}+{popup_y}")
            
            # Create a frame for better styling
            frame = tk.Frame(popup, bg='#f0f0f0', relief='solid', bd=1)
            frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Create entry
            entry = tk.Entry(frame, font=('Arial', 9), bd=0)
            entry.insert(0, str(current_value))
            entry.select_range(0, tk.END)  # Select all text
            entry.pack(fill='both', expand=True, padx=2, pady=2)
            entry.focus()
            
            # Make sure the popup is on top
            popup.lift()
            popup.focus_force()
            
            # Handle saving
            def save_value(evt=None):
                new_value = entry.get()
                try:
                    # Validate based on column type
                    if column == 'sequence':
                        new_value = int(new_value)
                        if new_value <= 0:
                            raise ValueError("Giá trị thứ tự phải dương")
                    elif column == 'sam':
                        new_value = float(new_value)
                        if new_value <= 0:
                            raise ValueError("Giá trị SAM phải dương")
                    
                    # Update treeview
                    new_values = list(values)
                    new_values[col_index] = new_value
                    self.ops_tree.item(item, values=new_values)
                    
                    # Update data model
                    item_index = self.ops_tree.index(item)
                    if column == 'sequence':
                        self.main_app.operations[item_index]['sequence'] = new_value
                    elif column == 'sam':
                        self.main_app.operations[item_index]['sam'] = new_value
                    
                    popup.destroy()
                except ValueError as e:
                    messagebox.showwarning("Lỗi", f"Giá trị không hợp lệ: {str(e)}")
                    entry.focus()
                    entry.select_range(0, tk.END)
            
            # Handle cancel
            def cancel_edit(evt=None):
                popup.destroy()
            
            # Bind events
            entry.bind("<Return>", save_value)
            entry.bind("<FocusOut>", save_value)
            entry.bind("<Escape>", cancel_edit)
    
    def show_worker_assignment_editor(self, event, item, column):
        """Show worker assignment dropdown editor"""
        # Get current value
        values = self.ops_tree.item(item, 'values')
        col_names = ['sequence', 'code', 'name', 'sam', 'machine', 'difficulty', 'assigned_1', 'assigned_2', 'assigned_3', 'assigned_4']
        col_index = col_names.index(column)
        current_value = values[col_index]
        
        # Create a dropdown at the cell position
        bbox = self.ops_tree.bbox(item, column)
        if bbox:  # Check if bbox is valid
            x, y, width, height = bbox
            popup = tk.Toplevel(self.ops_tree)
            popup.overrideredirect(True)
            popup.configure(bg='#f0f0f0')  # Light gray background
            
            # Calculate height based on font size (80% of font height for 10 items)
            font_height = 12  # Default font height
            popup_height = int(font_height * 0.8 * 10)  # Approximately 10 items high
            popup_width = int(width * 0.8)  # Reduce width by 20%
            
            # Position the popup
            popup_x = x + self.ops_tree.winfo_rootx()
            popup_y = y + self.ops_tree.winfo_rooty()
            popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
            
            # Create a frame for better styling
            frame = tk.Frame(popup, bg='#f0f0f0', relief='solid', bd=1)
            frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Get list of workers
            worker_names = [worker['name'] for worker in self.main_app.workers]
            # Add empty option for no assignment
            options = [''] + worker_names
            
            combo = ttk.Combobox(frame, values=options, state="readonly", font=('Arial', 9))
            combo.set(current_value)
            combo.pack(fill='both', expand=True, padx=2, pady=2)
            combo.focus()
            
            # Make sure the popup is on top
            popup.lift()
            popup.focus_force()
            
            # Handle selection
            def on_select(evt):
                new_value = combo.get()
                # Update treeview
                new_values = list(values)
                new_values[col_index] = new_value
                self.ops_tree.item(item, values=new_values)
                
                # Update data model
                item_index = self.ops_tree.index(item)
                # Update assigned worker field based on column
                worker_index = int(column.split('_')[1]) - 1  # Get worker index (0-3)
                
                # Initialize assigned_workers list if it doesn't exist
                if 'assigned_workers' not in self.main_app.operations[item_index]:
                    self.main_app.operations[item_index]['assigned_workers'] = ['', '', '', '']
                
                # Update the specific worker slot
                self.main_app.operations[item_index]['assigned_workers'][worker_index] = new_value
                
                popup.destroy()
            
            # Close popup when selection is made
            combo.bind("<<ComboboxSelected>>", on_select)
            
            # Force the dropdown to open after a short delay
            popup.after(10, lambda: combo.event_generate('<Button-1>'))

    def show_dropdown_editor(self, event, item, column):
        """Show dropdown editor for specific columns"""
        # Get current value
        values = self.ops_tree.item(item, 'values')
        col_names = ['sequence', 'code', 'name', 'sam', 'machine', 'difficulty']
        col_index = col_names.index(column)
        current_value = values[col_index]
        
        # Create a dropdown at the cell position
        bbox = self.ops_tree.bbox(item, column)
        if bbox:  # Check if bbox is valid
            x, y, width, height = bbox
            popup = tk.Toplevel(self.ops_tree)
            popup.overrideredirect(True)
            popup.configure(bg='#f0f0f0')  # Light gray background
            
            # Calculate height based on font size (80% of font height) and reduce width
            font_height = 12  # Default font height
            popup_height = int(font_height * 0.8 * 5)  # Approximately 5 items high
            popup_width = int(width * 0.8)  # Reduce width by 20%
            
            # Position the popup
            popup_x = x + self.ops_tree.winfo_rootx()
            popup_y = y + self.ops_tree.winfo_rooty()
            popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
            
            # Create a frame for better styling
            frame = tk.Frame(popup, bg='#f0f0f0', relief='solid', bd=1)
            frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Create dropdown based on column
            if column == 'machine':
                options = [
                    "Máy 1 kim",
                    "Máy 2 kim",
                    "Máy vắt sổ",
                    "Máy viền/Máy đánh bông",
                    "Máy chuyên dụng",
                    "Phụ/Ủi"
                ]
            elif column == 'difficulty':
                options = [
                    "Dễ",
                    "Trung bình",
                    "Cao"
                ]
            
            combo = ttk.Combobox(frame, values=options, state="readonly", font=('Arial', 9))
            combo.set(current_value)
            combo.pack(fill='both', expand=True, padx=2, pady=2)
            combo.focus()
            
            # Make sure the popup is on top
            popup.lift()
            popup.focus_force()
            
            # Handle selection
            def on_select(evt):
                new_value = combo.get()
                # Update treeview
                new_values = list(values)
                new_values[col_index] = new_value
                self.ops_tree.item(item, values=new_values)
                
                # Update data model
                item_index = self.ops_tree.index(item)
                if column == 'machine':
                    self.main_app.operations[item_index]['machine'] = new_value
                elif column == 'difficulty':
                    self.main_app.operations[item_index]['difficulty'] = new_value
                
                popup.destroy()
            
            # Không đóng popup khi mất focus, chỉ đóng khi chọn giá trị
            combo.bind("<<ComboboxSelected>>", on_select)
            # Loại bỏ binding <FocusOut> và <Escape> để popup không đóng khi mất focus
            
            # Force the dropdown to open after a short delay
            popup.after(10, lambda: combo.event_generate('<Button-1>'))
    
    def on_item_double_click(self, event):
        """Handle double-click on operation row - do nothing for now"""
        pass
    
    def add_operation(self):
        """Add a new operation"""
        try:
            sequence_str = self.op_sequence.get().strip()
            code = self.op_code.get().strip()
            name = self.op_name.get().strip()
            sam_str = self.op_sam.get().strip()
            machine = self.op_machine.get()
            difficulty = self.op_difficulty.get()
            
            # Kiểm tra dữ liệu đầu vào
            if not all([sequence_str, code, name, machine, sam_str]):
                messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
                return
                
            # Kiểm tra trùng lặp mã
            for op in self.main_app.operations:
                if op['code'] == code:
                    messagebox.showwarning("Cảnh báo", "Mã công đoạn đã tồn tại!")
                    return
            
            # Kiểm tra giá trị thứ tự
            try:
                sequence = int(sequence_str)
                if sequence <= 0:
                    messagebox.showwarning("Cảnh báo", "Giá trị thứ tự phải dương!")
                    return
            except ValueError:
                messagebox.showwarning("Cảnh báo", "Giá trị thứ tự phải là số nguyên!")
                return
            
            # Kiểm tra giá trị SAM
            try:
                sam = float(sam_str)
                if sam <= 0:
                    messagebox.showwarning("Cảnh báo", "Giá trị SAM phải dương!")
                    return
            except ValueError:
                messagebox.showwarning("Cảnh báo", "Giá trị SAM phải là số!")
                return
            
            # Thêm công đoạn mới
            self.main_app.operations.append({
                'sequence': sequence,
                'code': code,
                'name': name,
                'sam': sam,
                'machine': machine,
                'difficulty': difficulty if difficulty else '',
                'assigned_workers': ['', '', '', '']  # Add empty assigned workers list
            })
            
            # Cập nhật bảng hiển thị
            self.refresh_table()
            
            # Xóa các trường nhập
            self.op_sequence.delete(0, tk.END)
            self.op_code.delete(0, tk.END)
            self.op_name.delete(0, tk.END)
            self.op_sam.delete(0, tk.END)
            self.op_machine.set('')
            self.op_difficulty.set('')
            
            messagebox.showinfo("Thành công", "Đã thêm công đoạn mới!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm công đoạn: {str(e)}")
    
    def delete_operation(self):
        """Delete selected operations"""
        selected = self.ops_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn công đoạn cần xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(selected)} công đoạn?")
        if not confirm:
            return
        
        # Xóa theo thứ tự ngược để giữ đúng chỉ số
        items_to_delete = list(selected)
        items_to_delete.reverse()
        
        # Create a set of indices to delete for faster lookup
        indices_to_delete = set()
        for item in items_to_delete:
            indices_to_delete.add(self.ops_tree.index(item))
        
        # Delete operations in reverse order to maintain correct indices
        for i in sorted(indices_to_delete, reverse=True):
            del self.main_app.operations[i]
        
        # Refresh the table once after all deletions
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the operations table display"""
        # Clear all items at once
        for item in self.ops_tree.get_children():
            self.ops_tree.delete(item)
        
        # Insert all items at once (already sorted)
        for op in self.main_app.operations:
            # Get assigned workers (up to 4)
            assigned_workers = op.get('assigned_workers', ['', '', '', ''])
            # Ensure we have exactly 4 elements
            while len(assigned_workers) < 4:
                assigned_workers.append('')
            
            self.ops_tree.insert('', 'end', values=(
                op.get('sequence', ''), 
                op['code'], 
                op['name'], 
                op['sam'], 
                op['machine'],
                op.get('difficulty', ''),
                assigned_workers[0],  # assigned_1
                assigned_workers[1],  # assigned_2
                assigned_workers[2],  # assigned_3
                assigned_workers[3]   # assigned_4
            ))
    
    def sort_by_column(self, col):
        """Sort operations by column"""
        # Toggle sort order if clicking the same column
        if self.sort_column == col:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.sort_column = col
            self.sort_order = 'asc'
        
        self.apply_sorting()
        self.refresh_table()
    
    def apply_sorting(self):
        """Apply sorting to operations data"""
        col = self.sort_column
        order = self.sort_order
        
        # Define sort key function
        def sort_key(op):
            if col in ['sequence', 'sam']:
                # Numeric sort for sequence and SAM
                try:
                    return float(op.get(col, 0))
                except:
                    return 0
            else:
                # String sort for other columns
                return str(op.get(col, '')).lower()
        
        # Sort operations
        reverse = (order == 'desc')
        self.main_app.operations.sort(key=sort_key, reverse=reverse)
    
    def on_operation_double_click(self, event):
        """Handle double-click on operation row for editing"""
        item = self.ops_tree.selection()
        if not item:
            return
            
        # Get the selected operation index
        index = self.ops_tree.index(item)
        operation = self.main_app.operations[index]
        
        # Show edit dialog
        self.show_operation_edit_dialog(
            index, 
            operation.get('sequence', ''),
            operation['code'], 
            operation['name'], 
            operation['sam'], 
            operation['machine'],
            operation.get('difficulty', '')
        )
