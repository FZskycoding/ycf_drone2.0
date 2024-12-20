from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QTextEdit
)
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MainInterface(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller  # 傳入 DroneController

        self.setWindowTitle("Pixhawk 主界面")
        self.setGeometry(100, 100, 800, 600)

        # QStackedWidget 管理多頁
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 首頁和詳細資料頁
        self.home_page = self.create_home_page()
        self.detail_page = PixhawkMonitor(self.controller, self.go_to_home_page)

        # 添加到堆疊
        self.stack.addWidget(self.home_page)  # 索引 0
        self.stack.addWidget(self.detail_page)  # 索引 1

    def create_home_page(self):
        """創建首頁"""
        page = QWidget()
        layout = QVBoxLayout()

        # 地圖框顯示
        self.map_view = QWebEngineView()
        self.map_view.setMinimumHeight(400)
        self.current_lat = 25.033964  # 預設緯度（台北）
        self.current_lon = 121.564468  # 預設經度（台北）
        self.update_map_view()  # 初始加載地圖
        layout.addWidget(self.map_view)

        # 重新整理按鈕
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 200);
            }
        """)
        self.refresh_button.setParent(self.map_view)  # 設置為地圖的子元件
        self.refresh_button.move(740, 10)  # 調整位置（地圖右上角）
        self.refresh_button.clicked.connect(self.refresh_map)

        # 按鈕：連接 Pixhawk
        self.connect_button = QPushButton("連接到 Pixhawk")
        self.connect_button.setStyleSheet("font-size: 18px;")
        self.connect_button.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_button)

        # 按鈕：查看詳細資料
        view_details_button = QPushButton("查看詳細資料")
        view_details_button.setStyleSheet("font-size: 18px;")
        view_details_button.clicked.connect(self.go_to_detail_page)
        layout.addWidget(view_details_button)

        page.setLayout(layout)
        return page


    def update_map_view(self):
        """更新地圖視圖"""
        map_url = f"https://www.google.com/maps/@{self.current_lat},{self.current_lon},15z"
        self.map_view.setUrl(QUrl(map_url))


    def refresh_map(self):
        """重新整理地圖，抓取當前 Pixhawk 經緯度"""
        if self.controller.is_connected():
            gps = self.controller.get_gps_position()
            
            if gps:
                self.current_lat, self.current_lon, _ = gps
                self.update_map_view()
            else:
                print("無法獲取 GPS 資料，保持預設位置")
        else:
            print("Pixhawk 未連接")

    def toggle_connection(self):
        """切換 Pixhawk 的連接狀態"""
        if self.controller.is_connected():
            self.disconnect_pixhawk()
        else:
            self.connect_pixhawk()

    def connect_pixhawk(self):
        """連接到 Pixhawk"""
        result = self.controller.connect()
        if result:
            self.connect_button.setText("斷開與 Pixhawk 的連接")
        else:
            self.connect_button.setText("連接失敗，重試")

    def disconnect_pixhawk(self):
        """斷開與 Pixhawk 的連接"""
        self.controller.disconnect()
        self.connect_button.setText("連接到 Pixhawk")

    def go_to_detail_page(self):
        """切換到詳細資料頁面"""
        self.stack.setCurrentIndex(1)

    def go_to_home_page(self):
        """返回首頁"""
        self.stack.setCurrentIndex(0)


class PixhawkMonitor(QWidget):
    def __init__(self, controller, return_callback):
        super().__init__()
        self.controller = controller
        self.return_callback = return_callback

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 標籤顯示
        self.status_label = QLabel("狀態：未連接")
        self.layout.addWidget(self.status_label)

        self.attitude_display = QTextEdit("姿態數據：")
        self.attitude_display.setReadOnly(True)
        self.layout.addWidget(self.attitude_display)

        self.gps_display = QTextEdit("GPS 數據：")
        self.gps_display.setReadOnly(True)
        self.layout.addWidget(self.gps_display)

        self.satellites_display = QTextEdit("衛星數據：")
        self.satellites_display.setReadOnly(True)
        self.layout.addWidget(self.satellites_display)

        # 返回按鈕
        back_button = QPushButton("返回首頁")
        back_button.clicked.connect(self.return_callback)
        self.layout.addWidget(back_button)

        # 定時器更新數據
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def update_data(self):
        """更新 Pixhawk 數據"""
        if self.controller.is_connected():
            self.status_label.setText("狀態：已連接")

            attitude = self.controller.get_attitude()
            if attitude:
                roll, pitch, yaw = attitude
                self.attitude_display.setText(
                    f"姿態數據：\nRoll: {roll:.2f}°\nPitch: {pitch:.2f}°\nYaw: {yaw:.2f}°"
                )

            gps = self.controller.get_gps_position()
            if gps:
                latitude, longitude, altitude = gps
                self.gps_display.setText(
                    f"GPS 數據：\nLatitude: {latitude:.6f}\nLongitude: {longitude:.6f}\nAltitude: {altitude:.2f}m"
                )

            satellites = self.controller.get_satellites_visible()
            self.satellites_display.setText(f"衛星數據：{satellites}")
        else:
            self.status_label.setText("狀態：未連接")
            self.attitude_display.setText("等待姿態數據...")
            self.gps_display.setText("等待 GPS 數據...")
            self.satellites_display.setText("等待衛星數據...")
