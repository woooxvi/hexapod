"""
    Copyright (C) 2017 - PRESENT  Zhengyu Peng, https://zpeng.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    ----------

    `                      `
    -:.                  -#:
    -//:.              -###:
    -////:.          -#####:
    -/:.://:.      -###++##:
    ..   `://:-  -###+. :##:
           `:/+####+.   :##:
    .::::::::/+###.     :##:
    .////-----+##:    `:###:
     `-//:.   :##:  `:###/.
       `-//:. :##:`:###/.
         `-//:+######/.
           `-/+####/.
             `+##+.
              :##:
              :##:
              :##:
              :##:
              :##:
               .+:

"""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread, QFile
from PySide6.QtUiTools import QUiLoader

import psutil
import socket

from pathlib import Path
import json

from tcpclient import TCPClient
from btclient import BluetoothClient

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyApp, self).__init__()

        config_file = Path('config.json')
        if config_file.exists():
            self.config = json.load(open('config.json', 'r'))
        else:
            self.config = dict()
            json.dump(self.config, open('config.json', 'w+'))

        """Load UI"""
        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.init_ui()

        self.is_tcp_connected = False
        self.is_bluetooth_connected = False

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_changed
        )
        self.ui.button_Refresh.clicked.connect(
            self.on_interface_refresh_button_clicked
        )

        self.ui.buttonTcpConnect.clicked.connect(
            self.on_tcp_client_connect_button_clicked
        )

        self.ui.pushButton_RotateX.clicked.connect(
            self.on_rotatex_button_clicked
        )
        self.ui.pushButton_RotateY.clicked.connect(
            self.on_rotatey_button_clicked
        )
        self.ui.pushButton_RotateZ.clicked.connect(
            self.on_rotatez_button_clicked
        )
        self.ui.pushButton_Twist.clicked.connect(
            self.on_twist_button_clicked
        )
        self.ui.pushButton_Climb.clicked.connect(
            self.on_climb_button_clicked
        )
        self.ui.buttonShiftLeft.clicked.connect(
            self.on_shiftleft_button_clicked
        )
        self.ui.buttonTurnLeft.clicked.connect(
            self.on_turnleft_button_clicked
        )
        self.ui.buttonFastForward.clicked.connect(
            self.on_fastforward_button_clicked
        )
        self.ui.buttonForward.clicked.connect(
            self.on_forward_button_clicked
        )
        self.ui.buttonStandby.clicked.connect(
            self.on_standby_button_clicked
        )
        self.ui.buttonBackward.clicked.connect(
            self.on_backward_button_clicked
        )
        self.ui.buttonShiftRight.clicked.connect(
            self.on_shiftright_button_clicked
        )
        self.ui.buttonTurnRight.clicked.connect(
            self.on_turnright_button_clicked
        )

        # Bluetooth client
        self.ui.buttonBtConnect.clicked.connect(
            self.on_bt_client_connect_button_clicked
        )

        # self.ui.textBrowserMessage.installEventFilter(self)

        self.ui.show()

    def eventFilter(self, widget, event):
        if self.ui.textBrowserMessage.isEnabled():
            if (event.type() == QtCore.QEvent.KeyPress):
                key = event.key()
                if key == QtCore.Qt.Key_Up:
                    self.on_forward_button_clicked()
                elif key == QtCore.Qt.Key_Down:
                    self.on_backward_button_clicked()
                elif key == QtCore.Qt.Key_Left:
                    self.on_turnleft_button_clicked()
                elif key == QtCore.Qt.Key_Right:
                    self.on_turnright_button_clicked()
                elif key == QtCore.Qt.Key_A:
                    self.on_shiftleft_button_clicked()
                elif key == QtCore.Qt.Key_D:
                    self.on_shiftright_button_clicked()
                elif key == QtCore.Qt.Key_W:
                    self.on_forward_button_clicked()
                elif key == QtCore.Qt.Key_S:
                    self.on_backward_button_clicked()
                elif key == QtCore.Qt.Key_Space:
                    self.on_standby_button_clicked()

                return True
        return QtWidgets.QWidget.eventFilter(self, widget, event)

    def save_config(self):
        try:
            json.dump(self.config, open('config.json', 'w+'))
        except PermissionError as err:
            pass

    def init_ui(self):
        # Interface
        self.on_interface_refresh_button_clicked()

        self.ui.groupBox_Control.setEnabled(False)
        self.ui.textBrowserMessage.setEnabled(False)

        tcp_client_ip = self.config.get('TCP_Client_IP', '127.0.0.1')
        tcp_client_port = self.config.get('TCP_Client_Port', '1234')
        self.ui.lineEdit_TcpClientTargetIP.setText(tcp_client_ip)
        self.ui.lineEdit_TcpClientTargetPort.setText(tcp_client_port)

        # Bluetooth Client
        self.ui.lineEditBtMac.setText(
            self.config.get('Bluetooth_Client_MAC', ''))
        self.ui.lineEditBtPort.setText(
            self.config.get('Bluetooth_Client_Port', '10'))

        self.ui.status_bar.clearMessage()
        self.ui.status_bar.setStyleSheet('color: green')
        self.ui.status_bar.showMessage('● Idle')

    def on_rotatex_button_clicked(self):
        self.tcp_client.send('rotatex')
        self.append_message('rotatex')

    def on_rotatey_button_clicked(self):
        self.tcp_client.send('rotatey')
        self.append_message('rotatey')

    def on_rotatez_button_clicked(self):
        self.tcp_client.send('rotatez')
        self.append_message('rotatez')

    def on_twist_button_clicked(self):
        self.tcp_client.send('twist')
        self.append_message('twist')

    def on_climb_button_clicked(self):
        self.tcp_client.send('climb')
        self.append_message('climb')

    def on_shiftleft_button_clicked(self):
        self.tcp_client.send('shiftleft')
        self.append_message('shiftleft')

    def on_turnleft_button_clicked(self):
        self.tcp_client.send('leftturn')
        self.append_message('leftturn')

    def on_fastforward_button_clicked(self):
        self.tcp_client.send('fastforward')
        self.append_message('fastforward')

    def on_forward_button_clicked(self):
        self.tcp_client.send('forward')
        self.append_message('forward')

    def on_standby_button_clicked(self):
        self.tcp_client.send('standby')
        self.append_message('standby')

    def on_backward_button_clicked(self):
        self.tcp_client.send('backward')
        self.append_message('backward')

    def on_shiftright_button_clicked(self):
        self.tcp_client.send('shiftright')
        self.append_message('shiftright')

    def on_turnright_button_clicked(self):
        self.tcp_client.send('rightturn')
        self.append_message('rightturn')

    def on_interface_refresh_button_clicked(self):
        self.net_if = psutil.net_if_addrs()

        interface_idx = self.config.get('Interface', 0)
        self.ui.comboBox_Interface.clear()

        net_names = list(self.net_if.keys())
        net_if_stats = psutil.net_if_stats()

        for if_name in net_names:
            if not net_if_stats[if_name].isup:
                self.net_if.pop(if_name, None)
            else:
                self.ui.comboBox_Interface.addItem(if_name)

        if interface_idx >= self.ui.comboBox_Interface.count():
            self.ui.comboBox_Interface.setCurrentIndex(0)
        else:
            self.ui.comboBox_Interface.setCurrentIndex(interface_idx)

        for snicaddr in self.net_if[self.ui.comboBox_Interface.currentText()]:
            if snicaddr.family == socket.AF_INET:
                ipv4_add = snicaddr.address
                break
            else:
                ipv4_add = '0.0.0.0'

        self.ui.label_LocalIP.setText(ipv4_add)

        self.config['Interface'] = self.ui.comboBox_Interface.currentIndex()
        self.save_config()

    def on_interface_selection_changed(self):
        current_interface = self.ui.comboBox_Interface.currentText()

        if current_interface in self.net_if:
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    ipv4_add = snicaddr.address
                    break
                else:
                    ipv4_add = '0.0.0.0'
        else:
            return

        self.ui.label_LocalIP.setText(ipv4_add)
        self.config['Interface'] = self.ui.comboBox_Interface.currentIndex()
        self.save_config()

    # TCP Client
    def on_tcp_client_connect_button_clicked(self):
        if self.ui.buttonTcpConnect.text() == 'Connect':
            self.ui.buttonTcpConnect.setEnabled(False)
            self.ui.lineEdit_TcpClientTargetIP.setEnabled(False)
            self.ui.lineEdit_TcpClientTargetPort.setEnabled(False)

            self.tcp_client_thread = QThread()
            self.tcp_client = TCPClient(
                self.ui.lineEdit_TcpClientTargetIP.text(),
                int(self.ui.lineEdit_TcpClientTargetPort.text()))

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self.on_tcp_client_status_update)
            self.tcp_client.message.connect(self.on_tcp_client_message_ready)

            self.tcp_client.moveToThread(self.tcp_client_thread)

            self.tcp_client_thread.start()

            self.config['TCP_Client_IP'] = self.ui.lineEdit_TcpClientTargetIP.text()
            self.config['TCP_Client_Port'] = self.ui.lineEdit_TcpClientTargetPort.text()
            self.save_config()

        elif self.ui.buttonTcpConnect.text() == 'Disconnect':
            self.ui.buttonTcpConnect.setEnabled(False)
            self.tcp_client.close()

    def on_tcp_client_status_update(self, status, addr):
        if status == TCPClient.STOP:
            self.is_tcp_connected = False
            self.tcp_client.status.disconnect()
            self.tcp_client.message.disconnect()

            self.ui.buttonTcpConnect.setText('Connect')
            self.tcp_client_thread.quit()

            self.ui.button_Refresh.setEnabled(True)
            self.ui.comboBox_Interface.setEnabled(True)

            self.ui.lineEdit_TcpClientTargetIP.setEnabled(True)
            self.ui.lineEdit_TcpClientTargetPort.setEnabled(True)

            if not self.is_bluetooth_connected:
                self.ui.textBrowserMessage.setEnabled(False)
                self.ui.groupBox_Control.setEnabled(False)

            self.ui.status_bar.clearMessage()
            self.ui.status_bar.setStyleSheet('color: green')
            self.ui.status_bar.showMessage('● Idle')

        elif status == TCPClient.CONNECTED:
            self.is_tcp_connected = True
            self.on_bt_client_connect_button_clicked()
            self.ui.buttonTcpConnect.setText('Disconnect')

            self.ui.button_Refresh.setEnabled(False)
            self.ui.comboBox_Interface.setEnabled(False)

            self.ui.groupBox_Control.setEnabled(True)
            self.ui.textBrowserMessage.setEnabled(True)

            # self.ui.textBrowserMessage.setEnabled(True)
            # self.ui.textBrowserMessage.setFocus()

            self.ui.status_bar.clearMessage()
            self.ui.status_bar.setStyleSheet('color: green')
            self.ui.status_bar.showMessage(
                '● Connected to ' +
                self.ui.label_LocalIP.text() +
                ':'+self.ui.lineEdit_TcpClientTargetPort.text())

        self.ui.buttonTcpConnect.setEnabled(True)

    def on_tcp_client_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

        # Bluetooth Client
    def on_bt_client_connect_button_clicked(self):
        if self.ui.buttonBtConnect.text() == 'Connect':
            self.ui.buttonBtConnect.setEnabled(False)
            self.ui.lineEditBtMac.setEnabled(False)
            self.ui.lineEditBtPort.setEnabled(False)

            self.bt_client_thread = QThread()
            self.bt_client = BluetoothClient(
                self.ui.lineEditBtMac.text(),
                int(self.ui.lineEditBtPort.text()))

            self.bt_client_thread.started.connect(self.bt_client.start)
            self.bt_client.status.connect(self.on_bt_client_status_update)
            self.bt_client.message.connect(self.on_bt_client_message_ready)

            self.bt_client.moveToThread(self.bt_client_thread)

            self.bt_client_thread.start()

            self.config['Bluetooth_Client_MAC'] = self.ui.lineEditBtMac.text()
            self.config['Bluetooth_Client_Port'] = self.ui.lineEditBtPort.text(
            )
            self.save_config()

        elif self.ui.buttonBtConnect.text() == 'Disconnect':
            self.ui.buttonBtConnect.setEnabled(False)
            self.bt_client.close()

    def on_bt_client_status_update(self, status, addr):
        if status == BluetoothClient.STOP:
            self.is_bluetooth_connected = False
            self.bt_client.status.disconnect()
            self.bt_client.message.disconnect()

            self.ui.buttonBtConnect.setText('Connect')
            self.bt_client_thread.quit()

            self.ui.lineEditBtMac.setEnabled(True)
            self.ui.lineEditBtPort.setEnabled(True)

            if not self.is_tcp_connected:
                self.ui.textBrowserMessage.setEnabled(False)
                self.ui.groupBox_Control.setEnabled(False)

            # self.status['Bluetooth']['Client'] = '[CLIENT] Idle'

        elif status == BluetoothClient.CONNECTED:
            self.is_bluetooth_connected = True
            self.on_tcp_client_connect_button_clicked()
            self.ui.buttonBtConnect.setText('Disconnect')
            self.ui.groupBox_Control.setEnabled(True)
            self.ui.textBrowserMessage.setEnabled(True)

        self.ui.buttonBtConnect.setEnabled(True)

    def on_bt_client_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [Bluetooth Server] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def append_message(self, message):
        self.ui.textBrowserMessage.append(
            '<div><strong>— ' +
            'localhost' +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            message +
            '<br></div>')


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    sys.exit(app.exec())
