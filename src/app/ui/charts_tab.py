"""
Charts Tab UI Module
====================

This module contains the UI components for the charts tab.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class ChartsTab:
    """Charts tab UI component"""
    
    def __init__(self, parent, main_app, bg_color):
        self.parent = parent
        self.main_app = main_app
        self.bg_color = bg_color
        
        # Create the frame for this tab
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the charts tab UI"""
        # Frame biểu đồ với hiệu ứng card
        chart_frame = ttk.LabelFrame(self.frame, text="Biểu Đồ Cân Bằng", padding=10, style='Card.TLabelframe')
        chart_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.figure = Figure(figsize=(12, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Kết nối sự kiện click với canvas
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        
        # Vẽ biểu đồ mặc định
        self.plot_charts()
    
    def plot_charts(self):
        """Plot charts for visualization"""
        self.figure.clear()
        
        if not self.main_app.assignments:
            # Hiển thị thông báo nếu chưa có dữ liệu
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Chưa có dữ liệu để hiển thị\nHãy cân bằng chuyền trước', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_axis_off()
            self.figure.tight_layout()
            self.canvas.draw()
            return
        
        # Biểu đồ: Sản lượng từng công đoạn mỗi giờ với đường takt time
        # Nhóm các phân công theo tên công đoạn
        operation_assignments = {}
        for assignment in self.main_app.assignments:
            op_name = assignment['operation']
            operation_assignments.setdefault(op_name, []).append(assignment)

        # Đếm số lượng công đoạn mà mỗi công nhân thực hiện
        worker_operation_count = {}
        for assignment in self.main_app.assignments:
            worker_name = assignment['worker']
            worker_operation_count[worker_name] = worker_operation_count.get(worker_name, 0) + 1

        # Tính toán tổng sản lượng hàng giờ cho từng công đoạn và công nhân
        operation_worker_outputs = {}
        operation_outputs = {}
        for op_name, assignments in operation_assignments.items():
            operation_worker_outputs[op_name] = {}
            total_output = 0
            for assignment in assignments:
                worker_name = assignment['worker']
                # Tính sản lượng hàng giờ nếu công nhân chỉ làm một mình công đoạn này
                full_output = 3600 / assignment['actual_time'] if assignment['actual_time'] > 0 else 0
                # Chia sản lượng theo số lượng công đoạn công nhân đang thực hiện
                hourly_output = full_output / worker_operation_count[worker_name]
                operation_worker_outputs[op_name][worker_name] = hourly_output
                total_output += hourly_output
            operation_outputs[op_name] = total_output
        
        # Sắp xếp các công đoạn theo thứ tự sequence
        op_sequence_map = {}
        for op in self.main_app.operations:
            op_sequence_map[op['name']] = op.get('sequence', 0)
        
        sorted_operations = sorted(operation_outputs.keys(), key=lambda x: op_sequence_map.get(x, 0))
        
        operations = sorted_operations
        total_outputs = [operation_outputs[op] for op in sorted_operations]
        
        ax = self.figure.add_subplot(111)
        
        # Tạo stacked bar chart với màu solid không chói
        bottom_values = np.zeros(len(operations))
        
        # Lấy danh sách tất cả công nhân
        all_workers = set()
        for op_name in operations:
            if op_name in operation_worker_outputs:
                all_workers.update(operation_worker_outputs[op_name].keys())
        
        # Tạo bảng màu solid, đậm, đầm hơn cho từng công nhân
        solid_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5',
            '#393b79', '#5254a3', '#6b6ecf', '#9c9ede', '#637939',
            '#8ca252', '#b5cf6b', '#cedb9c', '#8c6d31', '#bd9e39'
        ]
        
        # Gán màu cho từng công nhân
        worker_colors = {}
        for i, worker in enumerate(sorted(all_workers)):
            worker_colors[worker] = solid_colors[i % len(solid_colors)]
        
        # Vẽ từng phần công nhân trong stacked bar
        worker_positions = {}  # Lưu vị trí để đặt nhãn
        
        for worker in sorted(all_workers):
            worker_outputs = []
            for op_name in operations:
                if op_name in operation_worker_outputs and worker in operation_worker_outputs[op_name]:
                    worker_outputs.append(operation_worker_outputs[op_name][worker])
                else:
                    worker_outputs.append(0)
            
            bars = ax.bar(range(len(operations)), worker_outputs, 
                         bottom=bottom_values, 
                         color=worker_colors.get(worker, '#4E79A7'), 
                         edgecolor='white', 
                         linewidth=0.7)
            
            # Lưu vị trí để đặt nhãn công nhân
            for j, (bottom, output) in enumerate(zip(bottom_values, worker_outputs)):
                if output > 0:  # Chỉ hiển thị nhãn nếu công nhân có sản lượng
                    worker_positions[(j, worker)] = bottom + output/2
            
            bottom_values = np.add(bottom_values, worker_outputs)
        
        # Thêm nhãn dữ liệu cho tổng sản lượng hàng giờ của từng công đoạn
        max_total_output = max(total_outputs) if total_outputs else 0
        for i, (op_name, total_output) in enumerate(zip(operations, total_outputs)):
            ax.text(i, total_output + max_total_output*0.01, f'{total_output:.1f}', 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Thêm nhãn tên công nhân vào giữa các đoạn cột
        for (op_index, worker), y_pos in worker_positions.items():
            # Chỉ hiển thị tên công nhân nếu đoạn đủ lớn để chứa văn bản
            if max_total_output > 0:
                worker_output = operation_worker_outputs[operations[op_index]][worker]
                if worker_output > max_total_output * 0.05:  # Nếu đoạn chiếm hơn 5% tổng chiều cao
                    # Tính toán màu chữ tương phản với màu nền
                    bg_color = worker_colors.get(worker, '#1f77b4')
                    # Chuyển đổi màu hex sang RGB
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    # Tính độ sáng của màu nền (luminance)
                    luminance = (0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]) / 255
                    # Chọn màu chữ tương phản (trắng cho nền tối, đen cho nền sáng)
                    text_color = 'white' if luminance < 0.5 else 'black'
                    
                    # Hiển thị tên công nhân và sản lượng hàng giờ trên các dòng riêng biệt
                    # Tên công nhân ở trên, sản lượng ở dưới
                    ax.text(op_index, y_pos + max_total_output * 0.015, worker, 
                           ha='center', va='bottom', fontsize=8, 
                           rotation=0, color=text_color, fontweight='bold')
                    ax.text(op_index, y_pos - max_total_output * 0.015, f"{worker_output:.1f}", 
                           ha='center', va='top', fontsize=8, 
                           rotation=0, color=text_color, fontweight='normal')
        
        # Cài đặt tiêu đề và nhãn với font sans-serif
        font = {'family': 'sans-serif', 'size': 10, 'style': 'normal'}
        ax.set_xlabel('Công Đoạn', fontdict=font)
        ax.set_ylabel('Sản lượng (sản phẩm/giờ)', fontdict=font)
        ax.set_title('Sản lượng Thực Tế Từng Công Đoạn (Stacked theo Công Nhân)', 
                    fontdict={'family': 'sans-serif', 'size': 12, 'weight': 'normal'})
        
        # Cài đặt ticks và labels
        ax.set_xticks(range(len(operations)))
        ax.set_xticklabels(operations, rotation=45, ha='right', fontdict=font)
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.grid(axis='y', alpha=0.3)
        
        # Thêm đường takt time nếu có
        if len(self.main_app.workers) > 0 and self.main_app.calculate_total_sam() > 0:
            try:
                total_sam = self.main_app.calculate_total_sam()
                takt_time = total_sam / len(self.main_app.workers)
                target_hourly_output = 3600 / takt_time if takt_time > 0 else 0
                ax.axhline(y=target_hourly_output, color='red', linestyle='--', linewidth=2, 
                          label=f'Mục tiêu: {target_hourly_output:.1f} sản phẩm/giờ')
                ax.legend(prop={'family': 'sans-serif', 'size': 9, 'style': 'normal'})
            except:
                pass  # Bỏ qua nếu không thể tính takt time
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_chart_click(self, event):
        """Handle click on chart to view more information"""
        if event.inaxes:
            # Có thể thêm xử lý khi click vào biểu đồ nếu cần
            pass
    
    def refresh_charts(self):
        """Refresh the charts display"""
        self.plot_charts()