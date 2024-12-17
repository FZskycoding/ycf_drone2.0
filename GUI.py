from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer


class PixhawkMonitor(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller  # 從外部傳入 DroneController

        self.setWindowTitle("Pixhawk Monitor")
        self.setGeometry(100, 100, 600, 400)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Labels and Display Widgets
        self.status_label = QLabel("Status: Disconnected")
        self.heartbeat_label = QLabel("Heartbeat: Not received")
        self.attitude_display = QTextEdit()
        self.attitude_display.setReadOnly(True)
        self.gps_display = QTextEdit()
        self.gps_display.setReadOnly(True)
        self.satellites_display = QTextEdit()
        self.satellites_display.setReadOnly(True)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(QLabel("Attitude Data:"))
        self.layout.addWidget(self.attitude_display)
        self.layout.addWidget(QLabel("GPS Data:"))
        self.layout.addWidget(self.gps_display)
        self.layout.addWidget(QLabel("Satellites Data:"))
        self.layout.addWidget(self.satellites_display)

        # Connect/Disconnect Button
        self.connect_button = QPushButton("Connect to Pixhawk")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.layout.addWidget(self.connect_button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

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
            self.status_label.setText("Status: Connected to Pixhawk")
            self.heartbeat_label.setText("Heartbeat: Received")
            self.timer.start(500)  # 更新數據間隔 500ms
            self.connect_button.setText("Disconnect from Pixhawk")
        else:
            self.status_label.setText("Status: Connection failed")

    def disconnect_pixhawk(self):
        """斷開與 Pixhawk 的連接"""
        self.controller.disconnect()
        self.timer.stop()
        self.status_label.setText("Status: Disconnected")
        self.heartbeat_label.setText("Heartbeat: Not received")
        self.attitude_display.clear()
        self.gps_display.clear()
        self.satellites_display.clear()
        self.connect_button.setText("Connect to Pixhawk")

    def update_data(self):
        """更新 Pixhawk 數據到 GUI"""
        attitude = self.controller.get_attitude()
        if attitude:
            roll, pitch, yaw = attitude
            self.attitude_display.setText(f"Roll: {roll:.2f}°\nPitch: {pitch:.2f}°\nYaw: {yaw:.2f}°")

        gps = self.controller.get_gps_position()
        if gps:
            latitude, longitude, altitude = gps
            self.gps_display.setText(f"Latitude: {latitude:.7f}\nLongitude: {longitude:.7f}\nAltitude: {altitude:.2f}m")

        satellites = self.controller.get_satellites_visible()
        if satellites is not None:
            self.satellites_display.setText(f"Satellites Visible: {satellites}")
        else:
            self.satellites_display.setText("Satellites Visible: 0")
