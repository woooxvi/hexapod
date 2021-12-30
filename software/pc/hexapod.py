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

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_change)
        self.ui.button_Refresh.clicked.connect(self.on_refresh_button_clicked)

        self.ui.button_TcpClient.clicked.connect(
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
        self.ui.pushButton_ShiftLeft.clicked.connect(
            self.on_shiftleft_button_clicked
        )
        self.ui.pushButton_TurnLeft.clicked.connect(
            self.on_turnleft_button_clicked
        )
        self.ui.pushButton_FastForward.clicked.connect(
            self.on_fastforward_button_clicked
        )
        self.ui.pushButton_Forward.clicked.connect(
            self.on_forward_button_clicked
        )
        self.ui.pushButton_Standby.clicked.connect(
            self.on_standby_button_clicked
        )
        self.ui.pushButton_Backward.clicked.connect(
            self.on_backward_button_clicked
        )
        self.ui.pushButton_ShiftRight.clicked.connect(
            self.on_shiftright_button_clicked
        )
        self.ui.pushButton_TurnRight.clicked.connect(
            self.on_turnright_button_clicked
        )

        self.ui.textBrowser_TcpClientMessage.installEventFilter(self)

        self.ui.show()

    def eventFilter(self, widget, event):
        if self.ui.textBrowser_TcpClientMessage.isEnabled():
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
        self.update_network_interfaces()

        self.ui.groupBox_Control.setEnabled(False)
        self.ui.textBrowser_TcpClientMessage.setEnabled(False)

        tcp_client_ip = self.config.get('TCP_Client_IP', '127.0.0.1')
        tcp_client_port = self.config.get('TCP_Client_Port', '1234')
        self.ui.lineEdit_TcpClientTargetIP.setText(tcp_client_ip)
        self.ui.lineEdit_TcpClientTargetPort.setText(tcp_client_port)

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

    def update_network_interfaces(self):
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

        current_interface = self.ui.comboBox_Interface.currentText()
        self.config['Interface'] = self.ui.comboBox_Interface.currentIndex()

        for snicaddr in self.net_if[current_interface]:
            if snicaddr.family == socket.AF_INET:
                ipv4_add = snicaddr.address
                break
            else:
                ipv4_add = '0.0.0.0'

        self.ui.label_LocalIP.setText(ipv4_add)

        self.save_config()

    def on_interface_selection_change(self):
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

    def on_refresh_button_clicked(self):
        self.update_network_interfaces()

    # TCP Client
    def on_tcp_client_connect_button_clicked(self):
        if self.ui.button_TcpClient.text() == 'Connect':
            self.ui.button_TcpClient.setEnabled(False)
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

        elif self.ui.button_TcpClient.text() == 'Disconnect':
            self.ui.button_TcpClient.setEnabled(False)
            self.tcp_client.close()

    def on_tcp_client_status_update(self, status, addr):
        if status == TCPClient.STOP:
            self.tcp_client.status.disconnect()
            self.tcp_client.message.disconnect()

            self.ui.button_TcpClient.setText('Connect')
            self.tcp_client_thread.quit()

            self.ui.lineEdit_TcpClientTargetIP.setEnabled(True)
            self.ui.lineEdit_TcpClientTargetPort.setEnabled(True)

            self.ui.textBrowser_TcpClientMessage.setEnabled(False)
            self.ui.groupBox_Control.setEnabled(False)
            self.ui.textBrowser_TcpClientMessage.setEnabled(False)

            self.ui.status_bar.clearMessage()
            self.ui.status_bar.setStyleSheet('color: green')
            self.ui.status_bar.showMessage('● Idle')

        elif status == TCPClient.CONNECTED:
            self.ui.button_TcpClient.setText('Disconnect')
            self.ui.groupBox_Control.setEnabled(True)
            self.ui.textBrowser_TcpClientMessage.setEnabled(True)

            self.ui.textBrowser_TcpClientMessage.setEnabled(True)
            self.ui.textBrowser_TcpClientMessage.setFocus()

            self.ui.status_bar.clearMessage()
            self.ui.status_bar.setStyleSheet('color: green')
            self.ui.status_bar.showMessage(
                '● Connected to ' +
                self.ui.label_LocalIP.text() +
                ':'+self.ui.lineEdit_TcpClientTargetPort.text())

        self.ui.button_TcpClient.setEnabled(True)

    def on_tcp_client_message_ready(self, source, msg):
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;"><strong>----- ' +
            source +
            ' -----</strong></span></p>')
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;">' +
            msg +
            '</span></p>')

    def append_message(self, message):
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><strong>----- ' +
            'this' +
            ' -----</strong></p>')
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;">' +
            message +
            '</p>')


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    sys.exit(app.exec())
