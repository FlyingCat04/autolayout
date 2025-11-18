"""
Workers Tab UI Module
=====================

This module contains the UI components for the workers management tab.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class WorkersTab:
    """Workers tab UI component"""
    
    def __init__(self, parent, main_app, bg_color):
        self.parent = parent
        self.main_app = main_app
        self.bg_color = bg_color
        self.sort_column = 'name'
        self.sort_order = 'asc'
        
        # Create the frame for this tab
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the workers tab UI"""
        # Frame nhập liệu với hiệu ứng card
        input_frame = ttk.LabelFrame(self.frame, text="Nhập Thông Tin Công Nhân", padding=15, style='Card.TLabelframe')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Hàng 1: Tên công nhân và khả năng xử lý độ khó
        ttk.Label(input_frame, text="Tên công nhân:").grid(row=0, column=0, sticky='w', pady=5, padx=(0, 5))
        self.worker_name = ttk.Entry(input_frame, width=25)
        self.worker_name.grid(row=0, column=1, sticky='w', pady=5, padx=(0, 15))
        
        ttk.Label(input_frame, text="Khả năng xử lý công đoạn có độ khó:").grid(row=0, column=2, sticky='w', pady=5, padx=(0, 5))
        self.worker_difficulty_handling = ttk.Combobox(input_frame, width=15, values=[
            "Dễ",
            "Trung bình", 
            "Cao"
        ])
        self.worker_difficulty_handling.grid(row=0, column=3, sticky='w', pady=5)
        self.worker_difficulty_handling.set("Dễ")  # Giá trị mặc định
        
        # Frame kỹ năng theo nhóm máy chức năng
        skills_frame = ttk.LabelFrame(input_frame, text="Độ Thông Thạo Theo Nhóm Máy (0-5)", padding=10, style='Card.TLabelframe')
        skills_frame.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(10, 10))
        
        # Cấu hình grid cho skills_frame
        skills_frame.columnconfigure(1, weight=1)
        skills_frame.columnconfigure(3, weight=1)
        
        # Thêm mô tả về thang điểm
        description = tk.Label(skills_frame, 
                              text="Thang điểm: 0 (Không biết dùng) - 1 (Đang học) - 2 (Cơ bản) - 3 (Trung bình) - 4 (Khá) - 5 (Giỏi)",
                              font=('Arial', 8, 'italic'),
                              fg='gray')
        description.grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 5))
        
        self.skill_entries = {}
        # Cập nhật theo phân loại máy móc theo chức năng
        machine_groups = [
            "Máy 1 kim",
            "Máy 2 kim",
            "Máy vắt sổ",
            "Máy viền/Máy đánh bông",
            "Máy chuyên dụng",
            "Phụ/Ủi"
        ]
        
        # Sắp xếp các trường kỹ năng theo 3 cột để gọn gàng hơn
        for i, machine_group in enumerate(machine_groups):
            row = (i // 3) + 1  # Bắt đầu từ hàng 1 vì hàng 0 là mô tả
            col = (i % 3) * 2
            ttk.Label(skills_frame, text=f"{machine_group}:").grid(row=row, column=col, sticky='w', padx=(0, 5), pady=3)
            # Sử dụng Combobox thay vì Entry cho độ thông thạo
            combo = ttk.Combobox(skills_frame, values=[str(i) for i in range(6)], width=5, state="readonly")
            combo.set("0")
            combo.grid(row=row, column=col+1, sticky='w', padx=(0, 15), pady=3)
            self.skill_entries[machine_group] = combo
        
        # Frame chứa các nút chức năng
        btn_frame = tk.Frame(input_frame, bg='white')
        btn_frame.grid(row=0, column=4, rowspan=2, sticky='nsew', padx=(20, 0), pady=5)
        
        # Căn giữa các nút theo chiều dọc
        btn_frame.columnconfigure(0, weight=1)
        btn_container = tk.Frame(btn_frame, bg='white')
        btn_container.pack(expand=True)
        
        ttk.Button(btn_container, text="Thêm Công Nhân", command=self.add_worker, style='Accent.TButton').pack(fill='x', pady=2)
        ttk.Button(btn_container, text="Import Excel", command=self.main_app.import_workers, style='TButton').pack(fill='x', pady=2)
        ttk.Button(btn_container, text="Export Excel", command=self.main_app.export_workers, style='TButton').pack(fill='x', pady=2)
        ttk.Button(btn_container, text="Xóa Công Nhân", command=self.delete_worker, style='Danger.TButton').pack(fill='x', pady=2)
        
        # Cấu hình grid cho input_frame
        input_frame.columnconfigure(0, weight=0)  # Labels
        input_frame.columnconfigure(1, weight=0)  # Entry fields
        input_frame.columnconfigure(2, weight=0)  # Labels
        input_frame.columnconfigure(3, weight=1)  # Entry fields
        input_frame.columnconfigure(4, weight=0)  # Button frame
        
        # Bảng hiển thị với hiệu ứng card
        table_frame = ttk.LabelFrame(self.frame, text="Danh Sách Công Nhân", padding=10, style='Card.TLabelframe')
        table_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Tạo treeview với scrollbar
        tree_container = tk.Frame(table_frame, bg='white')
        tree_container.pack(fill='both', expand=True)
        
        cols = ['name', 'difficulty'] + [f"skill_{i}" for i in range(6)]  # Thêm cột difficulty
        self.workers_tree = ttk.Treeview(tree_container, columns=cols, show='headings', height=12)
        self.workers_tree.heading('name', text='Tên', command=lambda: self.sort_by_column('name'))
        self.workers_tree.heading('difficulty', text='Xử lý độ khó', command=lambda: self.sort_by_column('difficulty'))  # Tiêu đề cột mới
        
        # Cập nhật tiêu đề cột theo nhóm máy chức năng
        machine_groups = [
            "Máy 1 kim",
            "Máy 2 kim",
            "Máy vắt sổ",
            "Máy viền/Máy đánh bông",
            "Máy chuyên dụng",
            "Phụ/Ủi"
        ]
        for i, machine_group in enumerate(machine_groups):
            self.workers_tree.heading(f'skill_{i}', text=machine_group[:15], command=lambda c=i: self.sort_by_column(f'skill_{c}'))
            self.workers_tree.column(f'skill_{i}', width=90)
        
        self.workers_tree.column('name', width=150)
        self.workers_tree.column('difficulty', width=100)  # Độ rộng cột mới
        
        # Style for treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        
        # Thêm sự kiện click để chỉnh sửa trực tiếp
        self.workers_tree.bind("<Double-1>", self.on_item_double_click)
        self.workers_tree.bind("<Button-1>", self.on_worker_item_click)
        
        # Tạo thanh cuộn dọc và ngang
        scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.workers_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal', command=self.workers_tree.xview)  # Di chuyển xuống dưới
        self.workers_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Bố trí các thành phần
        self.workers_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')  # Đặt ở dưới cùng
        
        # Load initial data
        self.refresh_table()
    
    def on_worker_item_click(self, event):
        """Handle single click on worker treeview items"""
        # Get the clicked region
        region = self.workers_tree.identify("region", event.x, event.y)
        column = self.workers_tree.identify_column(event.x)  # Sửa lỗi: chỉ cần truyền event.x
        row = self.workers_tree.identify_row(event.y)
        
        # Only handle cell clicks (not headings)
        if region == "cell" and row:
            # Get column name
            col_id = int(column[1:]) - 1  # Convert to 0-based index
            col_names = ['name', 'difficulty'] + [f'skill_{i}' for i in range(6)]
            if 0 <= col_id < len(col_names):
                col_name = col_names[col_id]
                
                # Only allow editing for specific columns
                if col_name in ['difficulty'] or col_name.startswith('skill_'):
                    self.show_worker_dropdown_editor(event, row, col_name)
    
    def show_worker_dropdown_editor(self, event, item, column):
        """Show dropdown editor for worker columns"""
        # Get current value
        values = self.workers_tree.item(item, 'values')
        col_names = ['name', 'difficulty'] + [f'skill_{i}' for i in range(6)]
        col_index = col_names.index(column)
        current_value = values[col_index]
        
        # Create a dropdown at the cell position
        bbox = self.workers_tree.bbox(item, column)
        if bbox:  # Check if bbox is valid
            x, y, width, height = bbox
            popup = tk.Toplevel(self.workers_tree)
            popup.overrideredirect(True)
            popup.configure(bg='#f0f0f0')  # Light gray background
            
            font_height = 12  # Default font height
            popup_height = int(font_height * 0.8 * 5)  # Approximately 5 items high
            popup_width = int(width * 0.8)  # Reduce width by 20%
            
            # Position the popup
            popup_x = x + self.workers_tree.winfo_rootx()
            popup_y = y + self.workers_tree.winfo_rooty()
            popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
            
            # Create a frame for better styling
            frame = tk.Frame(popup, bg='#f0f0f0', relief='solid', bd=1)
            frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Create dropdown based on column
            if column == 'difficulty':
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
                    self.workers_tree.item(item, values=new_values)
                    
                    # Update data model
                    item_index = self.workers_tree.index(item)
                    self.main_app.workers[item_index]['difficulty_handling'] = new_value
                    
                    popup.destroy()
                
                # Không đóng popup khi mất focus, chỉ đóng khi chọn giá trị
                combo.bind("<<ComboboxSelected>>", on_select)
                # Loại bỏ binding <FocusOut> và <Escape> để popup không đóng khi mất focus
                
                # Force the dropdown to open after a short delay
                popup.after(10, lambda: combo.event_generate('<Button-1>'))
            elif column.startswith('skill_'):
                # For skill columns, show a dropdown with values 0-5
                options = [str(i) for i in range(6)]  # 0, 1, 2, 3, 4, 5
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
                    self.workers_tree.item(item, values=new_values)
                    
                    # Update data model
                    item_index = self.workers_tree.index(item)
                    machine_groups = [
                        "Máy 1 kim",
                        "Máy 2 kim",
                        "Máy vắt sổ",
                        "Máy viền/Máy đánh bông",
                        "Máy chuyên dụng",
                        "Phụ/Ủi"
                    ]
                    skill_index = int(column.split('_')[1])
                    if skill_index < len(machine_groups):
                        machine_group = machine_groups[skill_index]
                        self.main_app.workers[item_index]['skills'][machine_group] = float(new_value)
                    
                    popup.destroy()
                
                # Không đóng popup khi mất focus, chỉ đóng khi chọn giá trị
                combo.bind("<<ComboboxSelected>>", on_select)
                # Loại bỏ binding <FocusOut> và <Escape> để popup không đóng khi mất focus
                
                # Force the dropdown to open after a short delay
                popup.after(10, lambda: combo.event_generate('<Button-1>'))
    
    def on_item_double_click(self, event):
        """Handle double-click on worker row - do nothing for now"""
        pass
    
    def add_worker(self):
        """Add a new worker"""
        try:
            name = self.worker_name.get().strip()
            difficulty_handling = self.worker_difficulty_handling.get()  # Lấy giá trị khả năng xử lý độ khó
            
            # Kiểm tra dữ liệu đầu vào
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên công nhân!")
                return
            
            # Kiểm tra trùng lặp tên
            for worker in self.main_app.workers:
                if worker['name'] == name:
                    messagebox.showwarning("Cảnh báo", "Tên công nhân đã tồn tại!")
                    return
            
            # Kiểm tra và lấy giá trị kỹ năng
            skills = {}
            for machine_group, widget in self.skill_entries.items():
                try:
                    # Support both Entry and Combobox
                    value = widget.get() if hasattr(widget, 'get') else widget.get()
                    score = float(value)
                    if not (0 <= score <= 5):
                        messagebox.showwarning("Cảnh báo", f"Điểm kỹ năng cho {machine_group} phải từ 0 đến 5!")
                        return
                    skills[machine_group] = score
                except ValueError:
                    messagebox.showwarning("Cảnh báo", f"Điểm kỹ năng cho {machine_group} phải là số!")
                    return
            
            # Thêm công nhân mới
            self.main_app.workers.append({
                'name': name,
                'difficulty_handling': difficulty_handling,  # Lưu khả năng xử lý độ khó
                'skills': skills
            })
            
            # Cập nhật bảng hiển thị
            self.refresh_table()
            
            # Xóa các trường nhập
            self.worker_name.delete(0, tk.END)
            self.worker_difficulty_handling.set("Dễ")  # Reset về mặc định
            for widget in self.skill_entries.values():
                if hasattr(widget, 'set'):
                    widget.set("1")
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, "1")
            
            messagebox.showinfo("Thành công", "Đã thêm công nhân mới!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm công nhân: {str(e)}")
    
    def delete_worker(self):
        """Delete selected workers"""
        selected = self.workers_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn công nhân cần xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(selected)} công nhân?")
        if not confirm:
            return
        
        # Xóa theo thứ tự ngược để giữ đúng chỉ số
        items_to_delete = list(selected)
        items_to_delete.reverse()
        
        # Create a set of indices to delete for faster lookup
        indices_to_delete = set()
        for item in items_to_delete:
            indices_to_delete.add(self.workers_tree.index(item))
        
        # Delete workers in reverse order to maintain correct indices
        for i in sorted(indices_to_delete, reverse=True):
            del self.main_app.workers[i]
        
        # Refresh the table once after all deletions
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the workers table display"""
        # Clear all items at once
        for item in self.workers_tree.get_children():
            self.workers_tree.delete(item)
        
        # Cập nhật theo nhóm máy chức năng
        machine_groups = [
            "Máy 1 kim",
            "Máy 2 kim",
            "Máy vắt sổ",
            "Máy viền/Máy đánh bông",
            "Máy chuyên dụng",
            "Phụ/Ủi"
        ]
        
        # Insert all items at once (already sorted)
        for worker in self.main_app.workers:
            values = [
                worker['name'],
                worker.get('difficulty_handling', 'Dễ')  # Thêm giá trị xử lý độ khó
            ] + [worker['skills'].get(m, 1) for m in machine_groups]
            self.workers_tree.insert('', 'end', values=values)
    
    def sort_by_column(self, col):
        """Sort workers by column"""
        # Toggle sort order if clicking the same column
        if self.sort_column == col:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.sort_column = col
            self.sort_order = 'asc'
        
        self.apply_sorting()
        self.refresh_table()
    
    def apply_sorting(self):
        """Apply sorting to workers data"""
        col = self.sort_column
        order = self.sort_order
        
        # Map column names to data structure
        col_mapping = {
            'name': 'name',
            'difficulty': 'difficulty_handling'
        }
        
        # Update machine groups list to match the current implementation
        machine_groups = [
            "Máy 1 kim",
            "Máy 2 kim", 
            "Máy vắt sổ",
            "Máy viền/Máy đánh bông",
            "Máy chuyên dụng",
            "Phụ/Ủi"
        ]
        
        # Define sort key function
        def sort_key(worker):
            if col in col_mapping:
                # Direct mapping for name and difficulty
                return str(worker.get(col_mapping[col], '')).lower()
            elif col.startswith('skill_'):
                # Skill column
                try:
                    index = int(col.split('_')[1])
                    if index < len(machine_groups):
                        machine = machine_groups[index]
                        return worker['skills'].get(machine, 0)
                    else:
                        return 0
                except (ValueError, IndexError):
                    return 0
            else:
                # Default case
                return str(worker.get(col, '')).lower()
        
        # Sort workers
        self.main_app.workers.sort(key=sort_key, reverse=(order == 'desc'))
        
        # Refresh the table display
        self.refresh_table()
    
    
    def on_worker_double_click(self, event):
        """Handle double-click on worker row for editing"""
        item = self.workers_tree.selection()
        if not item:
            return
            
        # Get the selected worker index
        index = self.workers_tree.index(item)
        worker = self.main_app.workers[index]
        
        # Show edit dialog
        self.show_worker_edit_dialog(
            index, 
            worker['name'], 
            worker['skills'],
            worker.get('difficulty_handling', 'Dễ')  # Truyền giá trị xử lý độ khó
        )

