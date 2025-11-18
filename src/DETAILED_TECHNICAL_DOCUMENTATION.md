# Tài liệu Kỹ Thuật Chi Tiết - LB Prototype

## 1. Tổng Quan Hệ Thống

LB Prototype là một ứng dụng desktop được thiết kế để tối ưu hóa phân công công việc trên dây chuyền sản xuất may mặc dựa trên thời gian tiêu chuẩn (SAM) và trình độ kỹ năng của công nhân. Ứng dụng giúp các nhà quản lý sản xuất phân bổ công việc một cách hiệu quả để đạt được hiệu suất tối ưu trên dây chuyền.

## 2. Kiến Trúc Ứng Dụng

### 2.1 Cấu trúc thư mục
```
LB prototype/
├── main.py                 # Điểm khởi động của ứng dụng
├── app/                    # Gói ứng dụng chính
│   ├── main_window.py     # Lớp cửa sổ chính điều phối toàn bộ ứng dụng
│   ├── ui/                # Các thành phần giao diện người dùng
│   │   ├── operations_tab.py
│   │   ├── workers_tab.py
│   │   ├── balancing_tab.py
│   │   └── charts_tab.py
│   ├── core/              # Chức năng cốt lõi
│   │   ├── data_manager.py
│   │   └── line_balancer.py
│   └── utils/             # Hàm tiện ích
```

### 2.2 Các thành phần chính
1. **Main Window** - Lớp trung tâm điều phối tất cả các thành phần khác
2. **UI Components** - Các tab giao diện người dùng
3. **Core Components** - Logic nghiệp vụ chính
4. **Utilities** - Các hàm hỗ trợ

## 3. Thuật Toán Cân Bằng Dây Chuyền

### 3.1 Mục tiêu cân bằng
1. Sử dụng tất cả các công nhân được nhập vào
2. Tất cả công đoạn được nhập vào phải được thực hiện
3. Phân bổ công nhân làm công đoạn phù hợp để tổng sản lượng trung bình hàng giờ của các công đoạn tương đương nhau, độ lệch sản lượng giữa 2 công đoạn có sản lượng lớn nhất và nhỏ nhất không quá 10%
4. Hiệu suất cân bằng dây chuyền phải lớn hơn hoặc bằng 85%

### 3.2 Các bước thực hiện thuật toán

#### Bước 1: Xử lý công nhân được chỉ định trước
Hàm: `_handle_assigned_workers()`
- Xử lý các công đoạn có công nhân được chỉ định trước
- Kiểm tra khả năng xử lý độ khó của công nhân
- Kiểm tra kỹ năng của công nhân với loại máy của công đoạn

#### Bước 2: Tính thời gian thực tế cho mỗi công nhân trên mỗi công đoạn
Hàm: `_calculate_worker_operation_times()`
- Tính toán thời gian thực tế thực hiện công đoạn cho từng công nhân
- Công thức: `actual_time = SAM / (efficiency / 100)`
- Hiệu suất được tính dựa trên kỹ năng của công nhân

#### Bước 3: Tính số công nhân cần thiết cho mỗi công đoạn
Hàm: `_calculate_operation_worker_requirements()`
- Công thức: `Required workers = Total workers * Operation SAM / Total SAM`
- Làm tròn đến số nguyên gần nhất
- Loại bỏ các giá trị dưới 0.5

#### Bước 4: Tính sản lượng mục tiêu và takt time
Hàm: `_calculate_target_output_and_takt_time()`
- Takt time = Tổng SAM / Tổng số công nhân
- Sản lượng mục tiêu = 3600 / Takt time

#### Bước 5: Phân bổ công nhân vào các công đoạn
Hàm: `_allocate_workers_to_operations()`
- Phân bổ công nhân dựa trên yêu cầu và khả năng
- Ưu tiên các công đoạn có ít công nhân có kỹ năng

#### Bước 6: Tối ưu hóa phân bổ
Hàm: `_optimize_allocations()`
- Di chuyển năng lực từ các công đoạn dư thừa sang bottleneck
- Đảm bảo sản lượng mục tiêu được duy trì

## 4. Các Hàm Quan Trọng

### 4.1 Trong LineBalancer (line_balancer.py)

#### balance_line()
Hàm chính thực hiện cân bằng dây chuyền:
- Kiểm tra điều kiện đầu vào
- Gọi tuần tự các bước của thuật toán
- Hiển thị kết quả và thống kê

#### _handle_assigned_workers()
Xử lý các công đoạn có công nhân được chỉ định:
- Kiểm tra kỹ năng công nhân
- Tạo phân công cho các công nhân được chỉ định trước

#### _calculate_worker_operation_times()
Tính thời gian thực tế cho mỗi công nhân:
- Dựa trên SAM và hiệu suất công nhân
- Trả về dictionary với thời gian cho từng cặp công nhân-công đoạn

#### _calculate_operation_worker_requirements()
Tính số công nhân cần thiết cho mỗi công đoạn:
- Dựa trên tỷ lệ SAM của công đoạn so với tổng SAM
- Trả về dictionary với số lượng yêu cầu cho từng công đoạn

#### _calculate_target_output_and_takt_time()
Tính takt time và sản lượng mục tiêu:
- Tính toán các chỉ số quan trọng cho quá trình cân bằng

#### _allocate_workers_to_operations()
Phân bổ công nhân vào công đoạn:
- Thực hiện phân bổ ban đầu dựa trên yêu cầu và khả năng
- Xử lý các ràng buộc về kỹ năng và độ khó

#### _optimize_allocations()
Tối ưu hóa phân bổ:
- Di chuyển công nhân giữa các công đoạn để cải thiện hiệu suất
- Đảm bảo đạt được mục tiêu cân bằng

#### _calculate_operation_outputs()
Tính sản lượng cho từng công đoạn:
- Tính sản lượng hàng giờ của từng công đoạn
- Trả về dictionary với sản lượng cho từng công đoạn

#### _calculate_efficiency_stats()
Tính toán thống kê hiệu suất:
- Tính các chỉ số thống kê về hiệu suất cân bằng
- Lưu trữ trong `efficiency_stats` của ứng dụng chính

### 4.2 Trong DataManager (data_manager.py)

#### import_operations()
Nhập dữ liệu công đoạn từ file Excel:
- Kiểm tra định dạng file
- Xác thực dữ liệu
- Thêm công đoạn vào danh sách

#### import_workers()
Nhập dữ liệu công nhân từ file Excel:
- Kiểm tra định dạng file
- Xác thực dữ liệu
- Thêm công nhân vào danh sách

#### export_results()
Xuất kết quả cân bằng:
- Tạo file Excel với kết quả và biểu đồ
- Bao gồm bảng phân công và biểu đồ trực quan

### 4.3 Trong ChartsTab (charts_tab.py)

#### plot_charts()
Vẽ biểu đồ trực quan:
- Tạo biểu đồ stacked bar cho sản lượng từng công đoạn
- Hiển thị takt time mục tiêu
- Gán màu cho từng công nhân

## 5. Các Biến và Cấu Trúc Dữ Liệu

### 5.1 Các biến trong ứng dụng chính (LineBalancingApp)
- `operations`: Danh sách công đoạn với thông tin chi tiết
- `workers`: Danh sách công nhân với kỹ năng
- `assignments`: Kết quả phân công công việc
- `balancing_results`: Dữ liệu kết quả để sắp xếp
- `efficiency_stats`: Thống kê hiệu suất

### 5.2 Cấu trúc dữ liệu công đoạn
```python
{
    'sequence': int,      # Thứ tự công đoạn
    'code': str,          # Mã công đoạn
    'name': str,          # Tên công đoạn
    'sam': float,         # Thời gian tiêu chuẩn (giây)
    'machine': str,       # Loại máy
    'difficulty': str     # Độ khó (Dễ, Trung bình, Cao)
}
```

### 5.3 Cấu trúc dữ liệu công nhân
```python
{
    'name': str,                    # Tên công nhân
    'difficulty_handling': str,     # Khả năng xử lý độ khó
    'skills': {                     # Kỹ năng với từng loại máy
        'machine_type': float       # Điểm kỹ năng (0-5)
    }
}
```

### 5.4 Cấu trúc dữ liệu phân công
```python
{
    'worker': str,          # Tên công nhân
    'operation': str,       # Tên công đoạn
    'sam': float,           # Thời gian tiêu chuẩn
    'actual_time': float    # Thời gian thực tế
}
```

## 6. Các Điều Kiện và Ràng Buộc

### 6.1 Điều kiện đầu vào
1. Cần có ít nhất 2 công nhân để thực hiện cân bằng dây chuyền
2. Tất cả công đoạn phải có SAM > 0
3. Công nhân phải có kỹ năng phù hợp với loại máy của công đoạn

### 6.2 Điều kiện hiệu suất
1. Độ lệch sản lượng giữa công đoạn cao nhất và thấp nhất không quá 10%
2. Hiệu suất cân bằng dây chuyền phải >= 85%
3. Tất cả công nhân phải được sử dụng

### 6.3 Ràng buộc phân công
1. Mỗi công nhân có thể thực hiện tối đa 3 công đoạn
2. Công đoạn phải liền kề nhau trong dây chuyền (trừ các loại máy đặc biệt)
3. Công nhân phải có kỹ năng phù hợp với loại máy
4. Công nhân phải có khả năng xử lý độ khó của công đoạn

### 6.4 Ràng buộc kỹ năng
- Kỹ năng được đánh giá từ 0-5:
  - 0: Không biết dùng
  - 1: Đang học
  - 2: Cơ bản
  - 3: Trung bình
  - 4: Khá
  - 5: Giỏi

### 6.5 Chuyển đổi hiệu suất
- 0 (Không biết dùng): 0% hiệu suất
- 1 (Đang học): 30% hiệu suất
- 2 (Cơ bản): 50% hiệu suất
- 3 (Trung bình): 65% hiệu suất
- 4 (Khá): 85% hiệu suất
- 5 (Giỏi): 100% hiệu suất

## 7. Các Thành Phần Giao Diện

### 7.1 Operations Tab
- Nhập và quản lý dữ liệu công đoạn
- Hiển thị danh sách công đoạn
- Cho phép thêm, sửa, xóa công đoạn

### 7.2 Workers Tab
- Nhập và quản lý dữ liệu công nhân
- Hiển thị danh sách công nhân và kỹ năng
- Cho phép thêm, sửa, xóa công nhân

### 7.3 Balancing Tab
- Hiển thị kết quả cân bằng
- Cho phép cấu hình thời gian làm việc
- Xuất kết quả và hiển thị thống kê

### 7.4 Charts Tab
- Hiển thị biểu đồ trực quan về kết quả cân bằng
- Biểu đồ stacked bar cho sản lượng từng công đoạn
- Đường takt time mục tiêu

## 8. Cách Chạy Ứng Dụng

### 8.1 Chạy phiên bản module hóa (khuyến nghị)
```bash
python main.py
```

### 8.2 Chạy phiên bản nguyên khối (để tham khảo)
```bash
python "proto 0.1.py"
```

## 9. Môi Trường Phát Triển

- Python 3.x
- Thư viện Tkinter (thường được cài đặt cùng với Python)
- NumPy cho tính toán số học
- Pandas cho xử lý dữ liệu
- Matplotlib cho biểu đồ
- XlsxWriter để xuất file Excel