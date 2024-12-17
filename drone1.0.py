import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit
)
from PyQt5.QtCore import QTimer
from pymavlink import mavutil


class PixhawkMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # MAVLink Connection
        self.master = None

    def toggle_connection(self):
        """Toggle connection to Pixhawk."""
        if self.master:  # Currently connected, so disconnect
            self.disconnect_pixhawk()
        else:  # Currently disconnected, so connect
            self.connect_pixhawk()

    def connect_pixhawk(self):
        """Connect to the Pixhawk device."""
        try:
            self.master = mavutil.mavlink_connection('COM4', baud=115200)
            self.master.wait_heartbeat()
            self.status_label.setText("Status: Connected to Pixhawk")
            self.heartbeat_label.setText("Heartbeat: Received")
            
            self.timer.start(500)  # Update data every 500ms
            self.connect_button.setText("Disconnect from Pixhawk")
        except Exception as e:
            self.status_label.setText(f"Status: Connection failed ({e})")

    def disconnect_pixhawk(self):
        """Disconnect from the Pixhawk device."""
        if self.master:
            self.timer.stop()  # Stop the timer
            self.master.close()  # Close the MAVLink connection
            self.master = None
            self.status_label.setText("Status: Disconnected")
            self.heartbeat_label.setText("Heartbeat: Not received")
            self.attitude_display.clear()
            self.gps_display.clear()
            self.satellites_display.clear()
            self.connect_button.setText("Connect to Pixhawk")

    def update_data(self):
        """Fetch data from Pixhawk and update the GUI."""
        if not self.master:
            return

        # Update Attitude
        attitude = self.get_attitude()
        if attitude:
            roll, pitch, yaw = attitude
            self.attitude_display.setText(f"Roll: {roll:.2f}°\nPitch: {pitch:.2f}°\nYaw: {yaw:.2f}°")

        # Update GPS
        gps = self.get_gps_position()
        if gps:
            latitude, longitude, altitude = gps
            self.gps_display.setText(f"Latitude: {latitude:.7f}\nLongitude: {longitude:.7f}\nAltitude: {altitude:.2f}m")

        # Update Satellites
        satellites = self.get_satellites_visible()
        if satellites is not None:
            self.satellites_display.setText(f"Satellites Visible: {satellites}")
        else:
            self.satellites_display.setText("Satellites Visible: 0")

    def get_attitude(self):
        """Retrieve attitude data from Pixhawk."""
        try:
            msg = self.master.recv_match(type="ATTITUDE", blocking=False)
            if msg:
                roll = math.degrees(msg.roll)
                pitch = math.degrees(msg.pitch)
                yaw = math.degrees(msg.yaw)
                return roll, pitch, yaw
        except Exception as e:
            self.status_label.setText(f"Error fetching attitude: {e}")
        return None

    def get_gps_position(self):
        """Retrieve GPS data from Pixhawk."""
        try:
            msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=False)
            if msg:
                latitude = msg.lat / 1e7
                longitude = msg.lon / 1e7
                altitude = msg.alt / 1000.0
                return latitude, longitude, altitude
        except Exception as e:
            self.status_label.setText(f"Error fetching GPS: {e}")
        return None

    def get_satellites_visible(self):
        """Retrieve the number of satellites visible from Pixhawk."""
        try:
            msg = self.master.recv_match(type="GPS_RAW_INT", blocking=False)
            if msg:
                return msg.satellites_visible
        except Exception as e:
            self.status_label.setText(f"Error fetching satellites: {e}")
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixhawkMonitor()
    window.show()
    sys.exit(app.exec_())
