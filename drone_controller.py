import sys
from PyQt5.QtWidgets import QApplication
from pymavlink import mavutil
from GUI import PixhawkMonitor


class DroneController:
    def __init__(self):
        self.master = None

    def connect(self):
        """連接到 Pixhawk"""
        try:
            self.master = mavutil.mavlink_connection('COM4', baud=115200)
            self.master.wait_heartbeat()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.master = None
            return False

    def disconnect(self):
        """斷開與 Pixhawk 的連接"""
        if self.master:
            self.master.close()
            self.master = None

    def is_connected(self):
        """檢查是否已連接"""
        return self.master is not None

    def get_attitude(self):
        """獲取姿態數據"""
        try:
            msg = self.master.recv_match(type="ATTITUDE", blocking=False)
            if msg:
                roll = msg.roll * 57.2958  # radians to degrees
                pitch = msg.pitch * 57.2958
                yaw = msg.yaw * 57.2958
                return roll, pitch, yaw
        except Exception as e:
            print(f"Error fetching attitude: {e}")
        return None

    def get_gps_position(self):
        """獲取 GPS 位置信息"""
        try:
            msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=False)
            if msg:
                latitude = msg.lat / 1e7
                longitude = msg.lon / 1e7
                altitude = msg.alt / 1000.0
                return latitude, longitude, altitude
        except Exception as e:
            print(f"Error fetching GPS: {e}")
        return None

    def get_satellites_visible(self):
        """獲取可見衛星數"""
        try:
            msg = self.master.recv_match(type="GPS_RAW_INT", blocking=False)
            if msg:
                return msg.satellites_visible
        except Exception as e:
            print(f"Error fetching satellites: {e}")
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = DroneController()
    window = PixhawkMonitor(controller)
    window.show()
    sys.exit(app.exec_())
