#!/usr/bin/env python3

import threading
import socket
from json import loads
from msvcrt import kbhit, getch
from numpy import random
from time import sleep
from math import floor



class Connector(object):
    def __init__(self, debug=False, verbose=False):  # type: (NeuroSky, bool, bool) -> None
        # Global            
        self._DEBUG = debug
        self._VERBOSE = verbose

        # Data Parameters
        self.raw_data = 0
        self.fft_data = []
        self.poor_signal_level = 0
        self._sampling_rate_counter = 0
        self._sampling_rate = 0
        self.is_open = True

        self.client_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

        # Keyboard initializer
        # self._init_thread(target=self.keypress_handler,
        #                   msg='Initialising keypress handler...')

        # Data Generator initializer
        self._init_thread(target=self._generate_data)



    def _init_thread(self, target, msg='', args=()):
        if self._VERBOSE and msg is not '':
            print(msg)
        threading.Thread(target=target, args=args).start()

    def _generate_sampling_rate(self):  # type: (NeuroSky) -> None
        while self.is_open:
            self._sampling_rate_counter = 0
            sleep(1)
            self._sampling_rate = self._sampling_rate_counter
            if self._VERBOSE:
                print('Sampling Rate: ', self._sampling_rate)

    def _generate_data(self):  # type: (NeuroSky) -> None
        if self._DEBUG:
            self._init_thread(target=self._generate_sampling_rate,
                              msg='Initialising timer...')
            while self.is_open:
                gaussian_num = floor(random.normal(0, 150, 1)[0])
                if -150 < gaussian_num < 150:
                    self.raw_data = gaussian_num
                    self.poor_signal_level = random.randint(0, 100)
                    self._sampling_rate_counter += 1

        else:
            try:
                self.client_socket.connect(('127.0.0.1', 13854))
                self.client_socket.sendall(bytes('{"enableRawOutput":true,"format":"Json"}'.encode('ascii')))
                self._init_thread(target=self._generate_sampling_rate,
                                  msg='Initialising timer...')
                if self._VERBOSE:
                    print('Retrieving data...')
                while self.is_open:
                    raw_bytes = self.client_socket.recv(1000)
                    data_set = (str(raw_bytes)[2:-3].split(r'\r'))
                    for data in data_set:
                        self._sampling_rate_counter += 1
                        try:
                            json_data = loads(data)
                            try:
                                self.raw_data = json_data['rawEeg']
                            except:
                                if len(json_data) > 3:
                                    self.poor_signal_level = self.raw_data = json_data['eSense']['poorSignalLevel']
                                else:
                                    self.poor_signal_level = self.raw_data = json_data['poorSignalLevel']
                        except:
                            continue
                    if self.poor_signal_level is 200 and self._VERBOSE:
                        print('Poor Connections!')
            except:
                print('An error occurred, are you connected?')
                self.close()

    def close(self):
        self.is_open = False
        try:
            self.client_socket.close()
        finally:
            print('Connection Closed!')


    # def keypress_handler(self):
    #     print('Press ESC to quit at any time!')
    #     while not self.is_closed:
    #         # if ESC key is press stop running and close socket
    #         if kbhit():
    #             key = ord(getch())
    #             if key is 27:
    #                 self.is_closed = True
    #                 break


if __name__ == '__main__':
    connector = Connector(debug=False, verbose=False)
    while connector.is_open:
        print(connector.raw_data)