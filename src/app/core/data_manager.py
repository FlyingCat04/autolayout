"""
Data Manager Core Module
========================

This module contains the data management functionality for importing and exporting data.
"""

from tkinter import filedialog, messagebox
import pandas as pd


class DataManager:
    """Data management component for handling import/export operations"""
    
    def __init__(self, main_app):
        self.main_app = main_app
    
    def import_operations(self):
        """Import operations from Excel file"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            try:
                df = pd.read_excel(filename)
                
                required_columns = ['sequence', 'code', 'name', 'sam', 'machine']
                if not all(col in df.columns for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    messagebox.showerror("Lỗi", f"File cần có các cột: {', '.join(missing_cols)}")
                    return
                
                # Kiểm tra dữ liệu
                invalid_rows = []
                for idx, row in df.iterrows():
                    # Kiểm tra sequence
                    try:
                        if row['sequence'] <= 0 or not isinstance(row['sequence'], (int, float)):
                            invalid_rows.append((idx+2, "Thứ tự phải là số nguyên dương"))
                    except:
                        invalid_rows.append((idx+2, "Thứ tự phải là số nguyên dương"))
                    
                    # Kiểm tra SAM
                    try:
                        if row['sam'] <= 0:
                            invalid_rows.append((idx+2, "SAM phải dương"))
                    except:
                        invalid_rows.append((idx+2, "SAM phải là số"))
                
                if invalid_rows:
                    error_msg = "Dữ liệu không hợp lệ ở các dòng:\n"
                    for row_num, error in invalid_rows[:5]:  # Hiển thị 5 lỗi đầu tiên
                        error_msg += f"Dòng {row_num}: {error}\n"
                    if len(invalid_rows) > 5:
                        error_msg += f"... và {len(invalid_rows)-5} lỗi nữa"
                    messagebox.showwarning("Lỗi Kiểm Tra Dữ Liệu", error_msg)
                    return
                
                imported_count = 0
                duplicate_count = 0
                
                # Pre-create a set of existing codes for faster lookup
                existing_codes = {op['code'] for op in self.main_app.operations}
                
                new_operations = []
                for _, row in df.iterrows():
                    # Kiểm tra trùng lặp
                    if row['code'] in existing_codes:
                        duplicate_count += 1
                        continue
                    
                    new_operations.append({
                        'sequence': int(row['sequence']),
                        'code': str(row['code']),
                        'name': str(row['name']),
                        'sam': float(row['sam']),
                        'machine': str(row['machine']),
                        'difficulty': str(row['difficulty']) if 'difficulty' in df.columns else ''
                    })
                    imported_count += 1
                
                # Add all new operations at once
                self.main_app.operations.extend(new_operations)
                
                self.main_app.refresh_operations_table()
                msg = f"Đã import thành công {imported_count} công đoạn."
                if duplicate_count > 0:
                    msg += f"\nBỏ qua {duplicate_count} công đoạn trùng lặp."
                messagebox.showinfo("Thành công", msg)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
    
    def import_workers(self):
        """Import workers from Excel file"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            try:
                df = pd.read_excel(filename)
                
                if 'name' not in df.columns:
                    messagebox.showerror("Lỗi", "File cần có cột 'name'")
                    return
                
                # Lấy các cột máy (trừ cột 'name')
                machine_cols = [col for col in df.columns if col != 'name' and col != 'difficulty_handling']
                
                imported_count = 0
                duplicate_count = 0
                
                # Pre-create a set of existing worker names for faster lookup
                existing_workers = {worker['name'] for worker in self.main_app.workers}
                
                new_workers = []
                for _, row in df.iterrows():
                    # Kiểm tra trùng lặp
                    if row['name'] in existing_workers:
                        duplicate_count += 1
                        continue
                    
                    skills = {}
                    for machine in machine_cols:
                        try:
                            score = float(row[machine]) if not pd.isna(row[machine]) else 0.0
                            if 0 <= score <= 5:  # Thay đổi phạm vi từ 0-10 thành 0-5
                                skills[machine] = score
                            else:
                                skills[machine] = 0.0  # Mặc định là 0 nếu ngoài phạm vi
                        except:
                            skills[machine] = 0.0  # Mặc định là 0 nếu không phải số
                    
                    new_workers.append({
                        'name': str(row['name']),
                        'difficulty_handling': str(row['difficulty_handling']) if 'difficulty_handling' in df.columns else 'Dễ',
                        'skills': skills
                    })
                    imported_count += 1
                
                # Add all new workers at once
                self.main_app.workers.extend(new_workers)
                
                self.main_app.refresh_workers_table()
                msg = f"Đã import thành công {imported_count} công nhân."
                if duplicate_count > 0:
                    msg += f"\nBỏ qua {duplicate_count} công nhân trùng lặp."
                messagebox.showinfo("Thành công", msg)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
    
    def export_workers(self):
        """Export workers to Excel file"""
        if not self.main_app.workers:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            try:
                # Prepare data for export
                export_data = []
                # Cập nhật theo nhóm máy chức năng
                machine_groups = [
                    "Máy 1 kim",
                    "Máy 2 kim",
                    "Máy vắt sổ",
                    "Máy viền/Máy đánh bông",
                    "Máy chuyên dụng",
                    "Phụ/Ủi"
                ]
                
                for worker in self.main_app.workers:
                    row = {
                        'name': worker['name'],
                        'difficulty_handling': worker.get('difficulty_handling', 'Dễ')
                    }
                    for machine_group in machine_groups:
                        row[machine_group] = worker['skills'].get(machine_group, 1)
                    export_data.append(row)
                
                df = pd.DataFrame(export_data)
                df.to_excel(filename, index=False)
                messagebox.showinfo("Thành công", f"Đã export dữ liệu vào {filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể export file: {str(e)}")
    
    def export_operations(self):
        """Export operations to Excel file"""
        if not self.main_app.operations:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            try:
                # Prepare data for export
                export_data = []
                for op in self.main_app.operations:
                    export_data.append({
                        'sequence': op.get('sequence', ''),
                        'code': op['code'],
                        'name': op['name'],
                        'sam': op['sam'],
                        'machine': op['machine'],
                        'difficulty': op.get('difficulty', '')
                    })
                
                df = pd.DataFrame(export_data)
                df.to_excel(filename, index=False)
                messagebox.showinfo("Thành công", f"Đã export dữ liệu vào {filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể export file: {str(e)}")
    
    def export_results(self):
        """Export balancing results to Excel file with table and chart image"""
        if not self.main_app.assignments:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            try:
                # Prepare assignment data for export
                export_data = []
                for assignment in self.main_app.assignments:
                    # Calculate efficiency as percentage
                    if assignment['actual_time'] > 0:
                        efficiency = (assignment['sam'] / assignment['actual_time']) * 100
                    else:
                        efficiency = 0
                    
                    export_data.append({
                        'Công nhân': assignment['worker'],
                        'Công đoạn': assignment['operation'],
                        'SAM (s)': assignment['sam'],
                        'Hiệu suất (%)': round(efficiency, 0),
                        'Thời gian thực tế (s)': assignment['actual_time']
                    })
                
                # Save the chart as an image
                chart_filename = filename.replace('.xlsx', '_chart.png')
                self.main_app.charts_tab.figure.savefig(chart_filename, dpi=300, bbox_inches='tight')
                
                # Create Excel file with xlsxwriter
                import xlsxwriter
                
                # Create a workbook and add a worksheet
                workbook = xlsxwriter.Workbook(filename)
                worksheet = workbook.add_worksheet('Kết quả cân bằng')
                
                # Add a format for the header
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Write the column headers
                headers = ['Công nhân', 'Công đoạn', 'SAM (s)', 'Hiệu suất (%)', 'Thời gian thực tế (s)']
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
                # Write the data
                for row, data in enumerate(export_data, start=1):
                    worksheet.write(row, 0, data['Công nhân'])
                    worksheet.write(row, 1, data['Công đoạn'])
                    worksheet.write(row, 2, data['SAM (s)'])
                    worksheet.write(row, 3, data['Hiệu suất (%)'])
                    worksheet.write(row, 4, data['Thời gian thực tế (s)'])
                
                # Set column widths
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 40)
                worksheet.set_column('C:E', 20)
                
                # Insert the chart image
                worksheet.insert_image('D2', chart_filename, {'x_scale': 0.8, 'y_scale': 0.8})
                
                # Set print options for A4
                worksheet.set_paper(9)  # A4
                worksheet.set_print_scale(85)
                worksheet.fit_to_pages(1, 1)
                worksheet.set_margins(left=0.3, right=0.3, top=0.3, bottom=0.3)
                
                workbook.close()
                
                # Remove the temporary chart image file
                import os
                os.remove(chart_filename)
                
                messagebox.showinfo("Thành công", f"Đã export kết quả vào {filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể export file: {str(e)}")
