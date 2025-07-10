# Hệ Thống Quản Lý Rừng (HTQLR) - Real-time Monitoring Dashboard

## Mô tả dự án

Hệ thống giám sát thời gian thực cho quản lý rừng, tích hợp với Firebase để thu thập dữ liệu và hiển thị dashboard với biểu đồ, bảng dữ liệu và phân tích nguy cơ sạt lở.

## Cấu trúc dự án

```
HTQLR/
├── src/
│   ├── main.py              # Script chính - thu thập dữ liệu và tạo dashboard
│   └── phan_tich_data.py    # Module phân tích và dự đoán nguy cơ sạt lở
├── data/
│   ├── firebase_data.csv    # Dữ liệu thời gian thực từ Firebase
│   ├── du_doan.csv          # Dữ liệu dự đoán nguy cơ sạt lở
│   ├── data.csv             # Dữ liệu đã được xử lý và chuẩn hóa
│   └── data.xlsx            # Dữ liệu Excel  gốc được thu thập từ kaggle
├── firebase/
│   └── quanlyrung-d69ec-firebase-adminsdk-fbsvc-0beb5e5d49.json  # Firebase credentials
├── output/
│   └── realtime_dashboard.html  # Dashboard HTML được tạo tự động
├── Truyen_data/             # Thư mục chứa code Arduino
├── Dockerfile               # Cấu hình Docker
├── Xu_ly_data.ipynb         # Notebook xử lý dữ liệu
└── README.md                # File này
```

##  Tính năng chính

### Dashboard thời gian thực
- **Biểu đồ đường**: Hiển thị dữ liệu 24 gần nhất.
- **Bảng dữ liệu**: Danh sách 24 dữ liệu mới nhất với thời gian, giá trị và mức độ sạt lở
- **Thống kê**: Giá trị hiện tại, tổng dữ liệu, giá trị trung bình, giá trị cao nhất
- **Tự động cập nhật**: Refresh mỗi 30 giây

### Phân tích nguy cơ sạt lở
- Dự đoán mức độ sạt lở dựa trên thời gian và lượng mưa
- Phân loại: **Thấp** / **Cao**
- Sử dụng thuật toán thống kê xác xuất dựa trên dữ liệu lịch sử

### Thu thập dữ liệu
- Kết nối Firebase Realtime Database
- Thu thập dữ liệu mỗi 30 giây
- Lưu trữ vào CSV với timestamp
- Tránh dữ liệu trùng lặp

## 🛠️ Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- pip
- Kết nối internet

### Cài đặt thủ công

1. **Clone repository**
```bash
cd HTQLR
```

2. **Cài đặt dependencies**
```bash
pip install firebase-admin pandas
```

3. **Chạy ứng dụng**
```bash
python src/main.py
```

### Sử dụng Docker

1. **Build image**
```bash
docker build -t htqlr .
```

2. **Chạy container**
```bash
docker run -p 8000:8000 htqlr
```

## Sử dụng

### Khởi động hệ thống
1.Cắm esp được nạp code trong `Truyen_data/Truyen_data_den_server.ino`
   -gui.ino và Nhan.ino là 2 file mô phỏng giao tiếp truyền thông tin giữa 2 esp qua modul Hc12
   - `Truyen_data\Truyen_data_den_server.ino` mô phỏng data được gửi đến sever qua firebase bằng các tạo ngẫu nhiên các giá trị từ 0 đến 104
2. Chạy script `src/main.py`
3. Hệ thống sẽ tự động:
   - Kết nối Firebase
   - Thu thập dữ liệu
   - Tạo dashboard HTML
   - Mở trình duyệt với dashboard

### Truy cập dashboard
- **URL**: `http://localhost:8000/output/realtime_dashboard.html`
- **Tự động mở**: Trình duyệt sẽ mở tự động khi khởi động
- **Cập nhật**: Dashboard tự động refresh mỗi 30 giây

### Cấu trúc dữ liệu

#### Firebase Data Format
```json
{
  "data": "14h30:150"
}
```
- `14h30`: Thời gian (giờ:phút)
- `150`: Giá trị lượng mưa

#### CSV Output Format
```csv
Thời gian,Giá trị,Timestamp
14h30,150,2024-01-15 14:30:00
```

## 🔧 Cấu hình

### Firebase Setup
1. Tạo project Firebase
2. Tạo Realtime Database
3. Tạo Service Account và download JSON key
4. Đặt file JSON vào thư mục `firebase/`

### Cấu hình đường dẫn
Trong `src/main.py`:
```python
DATA_FILE = "data/firebase_data.csv"
HTML_FILE = "output/realtime_dashboard.html"
cred = credentials.Certificate("firebase/quanlyrung-d69ec-firebase-adminsdk-fbsvc-0beb5e5d49.json")
```

## Phân tích dữ liệu

### Module `phan_tich_data.py`
- **Function**: `du_doan(gio, ngay, thang, luong_mua)`
- **Input**: Thời gian và lượng mưa
- **Output**: Mức độ nguy cơ sạt lở (Thấp/Cao)
- **Logic**: So sánh với dữ liệu lịch sử trong `du_doan.csv`

### Dữ liệu dự đoán
File `data/du_doan.csv` chứa:
- `thoi_diem`: Thời điểm (MM-DD HHh)
- `xac_suat_satlo`: Xác suất sạt lở
- `luong_mua_tb_khi_satlo`: Lượng mưa trung bình khi sạt lở
- `luong_mua_min_satlo`: Lượng mưa tối thiểu khi sạt lở

https://github.com/AnhTuan2003m