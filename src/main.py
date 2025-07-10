import firebase_admin
from firebase_admin import credentials, db
import json
import time
from datetime import datetime
import csv
import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socket
from phan_tich_data import du_doan

# Khởi tạo Firebase với service account key
cred = credentials.Certificate("firebase/quanlyrung-d69ec-firebase-adminsdk-fbsvc-0beb5e5d49.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://quanlyrung-d69ec-default-rtdb.firebaseio.com/'
})

# File để lưu dữ liệu
DATA_FILE = "data/firebase_data.csv"
HTML_FILE = "output/realtime_dashboard.html"

# Đọc 24 dòng cuối cùng từ file CSV
def get_last_24_from_csv():
    times, values = [], []
    if not os.path.exists(DATA_FILE):
        return times, values
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = list(csv.DictReader(f))
        # Sắp xếp từ mới đến cũ (dòng cuối là mới nhất)
        last_rows = data[-24:] if len(data) >= 24 else data
        for row in last_rows:
            times.append(row['Thời gian'])
            values.append(int(row['Giá trị']))
    return times, values

def parse_firebase_data(data):
    try:
        if isinstance(data, dict) and 'data' in data:
            du_lieu = (data['data']).split(':')
            if len(du_lieu) == 2:
                thoi_gian = du_lieu[0]  
                gia_tri = int(du_lieu[1])  
                return thoi_gian, gia_tri
        return None, None
    except Exception as e:
        print(f"Lỗi parse dữ liệu: {e}")
        return None, None

def save_data_to_csv(time_part, value_part):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        # Kiểm tra xem thời gian + ngày này đã tồn tại chưa
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # So sánh cả thời gian và ngày
                    if row['Thời gian'] == time_part and row['Timestamp'].startswith(today):
                        print(f"Bỏ qua dữ liệu trùng lặp: {time_part} ({today})")
                        return

        # Tạo file mới nếu chưa tồn tại
        file_exists = os.path.exists(DATA_FILE)

        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Ghi header nếu file mới
            if not file_exists:
                writer.writerow(['Thời gian', 'Giá trị', 'Timestamp'])

            # Ghi dữ liệu
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([time_part, value_part, timestamp])

    except Exception as e:
        print(f"Lỗi lưu dữ liệu: {e}")

def doc_firebase():
    """Đọc dữ liệu từ Firebase"""
    try:
        ref = db.reference('data')
        data = ref.get()
        if data:
            print(f"Dữ liệu từ Firebase: {data}")
            time_part, value_part = parse_firebase_data(data)
            if time_part and value_part is not None:
                print(f"   Thời gian: {time_part}")
                print(f"   Giá trị: {value_part}")
                # Lưu vào file CSV
                save_data_to_csv(time_part, value_part)
                return time_part, value_part          
        else:
            return None, None
            
    except Exception as e:
        return None, None



def create_html_dashboard():
    """Tạo file HTML dashboard"""
    times, values = get_last_24_from_csv()
    html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firebase Real-time Dashboard</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .dashboard-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .status-connected {{
            background-color: #28a745;
            animation: pulse 2s infinite;
        }}
        
        .status-disconnected {{
            background-color: #dc3545;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .stats-card {{
            text-align: center;
            padding: 20px;
            margin: 10px 0;
        }}
        
        .stats-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #764ba2;
        }}
        
        .stats-label {{
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="dashboard-card p-4">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="mb-0">
                                <i class="fas fa-chart-line me-2"></i>
                                Firebase Real-time Dashboard
                            </h1>
                            <p class="text-muted mb-0">Theo dõi dữ liệu theo thời gian thực</p>
                        </div>
                        <div class="text-end">
                            <div class="mb-2">
                                <span class="status-indicator status-connected" id="connectionStatus"></span>
                                <span id="connectionText">Đang kết nối...</span>
                            </div>
                            <div class="text-muted">
                                <small id="lastUpdate">Chưa có dữ liệu</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="dashboard-card stats-card">
                    <div class="stats-number" id="currentValue">{values[-1] if values else '--'}</div>
                    <div class="stats-label">Giá trị hiện tại</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="dashboard-card stats-card">
                    <div class="stats-number" id="totalData">{sum(1 for _ in open(DATA_FILE, encoding='utf-8'))-1 if os.path.exists(DATA_FILE) else 0}</div>
                    <div class="stats-label">Tổng dữ liệu</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="dashboard-card stats-card">
                    <div class="stats-number" id="avgValue">{round(sum(values)/len(values),1) if values else '--'}</div>
                    <div class="stats-label">Giá trị trung bình (24 dữ liệu)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="dashboard-card stats-card">
                    <div class="stats-number" id="maxValue">{max(values) if values else '--'}</div>
                    <div class="stats-label">Giá trị cao nhất (24 dữ liệu)</div>
                </div>
            </div>
        </div>

        <!-- Chart -->
        <div class="row">
            <div class="col-12">
                <div class="dashboard-card p-4">
                    <h4 class="mb-3">
                        <i class="fas fa-chart-area me-2"></i>
                        Biểu đồ dữ liệu theo giờ
                    </h4>
                    <div class="chart-container">
                        <canvas id="dataChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="dashboard-card p-4">
                    <h4 class="mb-3">
                        <i class="fas fa-table me-2"></i>
                        Dữ liệu gần đây (24 dữ liệu mới nhất)
                    </h4>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Thời gian</th>
                                    <th>Giá trị</th>
                                    <th>Mức độ sạt lở</th>
                                </tr>
                            </thead>
                            <tbody id="dataTable">
                                {generate_table_rows(times, values)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        const chartLabels = {json.dumps(times, ensure_ascii=False)};
        const chartValues = {json.dumps(values, ensure_ascii=False)};
        const chartData = {{labels: chartLabels,datasets: [{{label: 'Giá trị',data: chartValues,borderColor: '#667eea',backgroundColor: 'rgba(102, 126, 234, 0.1)',borderWidth: 3,fill: true,tension: 0.4,pointBackgroundColor: '#764ba2',pointBorderColor: '#fff',pointBorderWidth: 2,pointRadius: 6}}]}};
        const ctx = document.getElementById('dataChart').getContext('2d');
        const dataChart = new Chart(ctx, {{type: 'line',data: chartData,options: {{responsive: true,maintainAspectRatio: false,plugins: {{legend: {{display: false}},tooltip: {{mode: 'index',intersect: false,backgroundColor: 'rgba(0, 0, 0, 0.8)',titleColor: '#fff',bodyColor: '#fff',borderColor: '#667eea',borderWidth: 1}}}},scales: {{x: {{title: {{display: true,text: 'Thời gian'}},grid: {{color: 'rgba(0, 0, 0, 0.1)'}}}},y: {{beginAtZero: true,title: {{display: true,text: 'Giá trị'}},grid: {{color: 'rgba(0, 0, 0, 0.1)'}}}}}},interaction: {{mode: 'nearest',axis: 'x',intersect: false}}}}}});
        setInterval(() => {{location.reload();}}, 30000);
    </script>
</body>
</html>
"""
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    

def generate_table_rows(times, values):
    """Tạo HTML cho bảng dữ liệu"""
    if not times:
        return '<tr><td colspan="3" class="text-center text-muted">Chưa có dữ liệu</td></tr>'
    rows = []
    for time_str, value in zip(times, values):
        # Tách giờ, ngày, tháng từ time_str (giả sử định dạng 'HHhMM' hoặc 'HHh')
        try:
            gio = int(time_str.split('h')[0])
        except:
            gio = 0
        now = datetime.now()
        ngay = now.day
        thang = now.month
        from phan_tich_data import du_doan
        muc_do = du_doan(gio, ngay, thang, value)
        rows.append(f'<tr><td>{time_str}</td><td><strong>{value}</strong></td><td>{muc_do}</td></tr>')
    return '\n'.join(rows)


def start_web_server():
    try:
        # Tìm port trống
        port = 8000
        while port < 8010:
            try:
                server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
                break
            except OSError:
                port += 1
        
        print(f"server đang chạy tại: http://localhost:{port}")
        print(f"Dashboard: http://localhost:{port}/{HTML_FILE}")
        
        # Mở trình duyệt
        webbrowser.open(f'http://localhost:{port}/{HTML_FILE}')
        
        # Chạy server trong thread riêng
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        return server, port
        
    except Exception as e:
        print(f"Lỗi khởi động web server: {e}")
        return None, None


def realtime_monitor():  
    # Tải dữ liệu từ file CSV nếu có
    times, values = get_last_24_from_csv()
    
    # Khởi động web server
    server, port = start_web_server()
    if not server:
        print("Không thể khởi động web server")
        return
    
    # Tạo dashboard HTML ban đầu
    create_html_dashboard()
    
    last_data = None
    data_count = 0
    
    try:
        while True:
            current_data = doc_firebase()
            
            if current_data and current_data != last_data:
                time_part, value_part = current_data
                print(f"{datetime.now().strftime('%H:%M:%S')} - {time_part}: {value_part}")
                last_data = current_data
                data_count += 1
                
                # Cập nhật dashboard HTML sau mỗi dữ liệu mới
                create_html_dashboard()
                
            time.sleep(30)  # Chờ 30 giây để giảm nhiễu
            
    except KeyboardInterrupt:
        print(f"\nDừng monitor. Tổng cộng {data_count} dữ liệu")
        if server:
            server.shutdown()
            print("Đã dừng web server")

# Chạy chương trình
if __name__ == "__main__":
    realtime_monitor() 