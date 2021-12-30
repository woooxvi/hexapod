import socket
import errno
from threading import Thread
import json


class TCPServer(Thread):
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2
    STOP = 3

    SIG_NORMAL = 0
    SIG_STOP = 1
    SIG_DISCONNECT = 2

    def __init__(self, out_cmd_queue):
        self.cmd_queue = out_cmd_queue

        with open('./config.json', 'r') as read_file:
            self.config = json.load(read_file)

        self.ip = '192.168.1.127'
        self.port = 1234
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.signal = self.SIG_NORMAL

    def run(self):
        try:
            self.tcp_socket.bind((self.ip, self.port))
            self.tcp_socket.listen(1)
            print('TCP listening')
        except OSError as err:
            # print('emit tcp server error')
            # self.status.emit(self.STOP, '')
            pass
        else:
            # self.status.emit(self.LISTEN, '')
            while True:
                # Wait for a connection
                # print('wait for a connection')
                # self.status.emit(self.LISTEN, '')
                try:
                    self.connection, addr = self.tcp_socket.accept()
                    # self.connection.setblocking(False)
                    # self.connection.settimeout(1)
                    print('New connection')
                except socket.timeout as t_out:
                    pass
                else:
                    while True:
                        # print('waiting for data')
                        # if self.signal == self.SIG_NORMAL:
                        try:
                            data = self.connection.recv(4096)
                        except socket.error as e:
                            err = e.args[0]
                            # if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            #     if self.current_motion is not None:
                            #         self.move(self.current_motion, 0.005)
                            #     else:
                            #         time.sleep(1)
                            #         print('No data available')
                            #     continue
                            # else:
                            # a "real" error occurred
                            print(e)
                            break
                            # sys.exit(1)
                        else:
                            if data:
                                self.cmd_queue.put(data.decode())
                                # move_routine(self, path, interval)
                                # self.message.emit(
                                #     addr[0]+':'+str(addr[1]),
                                #     data.decode())
                            else:
                                # self.status.emit(self.LISTEN, '')
                                self.cmd_queue.put('standby')
                                break
                        # elif self.signal == self.SIG_DISCONNECT:
                        #     self.signal = self.SIG_NORMAL
                        #     # self.connection.close()
                        #     # self.status.emit(self.LISTEN, '')
                        #     break

        finally:
            self.tcp_socket.close()
            self.cmd_queue.put('standby')
            # self.status.emit(self.STOP, '')
            print('exit')
