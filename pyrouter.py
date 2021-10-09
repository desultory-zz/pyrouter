#!/usr/bin/env python3

from WebServer import WebServerThread
from xml.etree import ElementTree as ET
import socket

class WSController():
    def __init__(self, debug = False):
        self.debug = debug
        self.init_webserver_thread()
        self.generate_menu()

    def init_webserver_thread(self):
        if self.debug:
            print("Initializing webserver thread object")
        self.wst = WebServerThread(debug = self.debug)
        if hasattr(self, "port"):
            self.wst.set_port(self.port)
        if hasattr(self, "ip"):
            self.wst.set_address(self.ip)

    def generate_menu(self):
        menu = {}
        menu['1'] = ["Start Webserver", self.wst.start_webserver]
        menu['2'] = ["Stop Webserver", self.wst.stop]
        menu['3'] = ["Kill thread", self.wst.kill]
        menu['4'] = ["Set port", self.set_port]
        menu['5'] = ["Set IP", self.set_ip]
        self.menu = menu

    def get_input(self):
        try:
            selection = input(">")
        except KeyboardInterrupt:
            self.clean_exit()
        if selection == "q" or selection.lower() == "quit":
            self.clean_exit()
        if selection in self.menu.keys():
            return selection
        else:
            print("Invalid choice")
            return None
    
    def process_choice(self, choice):
        if self.debug:
            print(f"Selected choice:{choice} mapped function:{self.menu[choice][1]}")
        self.menu[choice][1]()

    def display_menu(self):
        menu_options = self.menu.keys()
        for entry in menu_options:
            print(f'{entry} {self.menu[entry][0]}')
        
    def menu_loop(self):
        while(True):
            self.display_menu()
            while (choice := self.get_input()) != None:
                self.process_choice(choice)

    def clean_exit(self):
        try:
            if isinstance(self.wst, WebServerThread):
                self.wst.kill()
                if self.wst.is_alive():
                    self.wst.join()
        except AttributeError:
            pass
        quit()
        
    def get_int_input(self, prompt = ">"):
        try:
            i = input(prompt)
            val = int(i)
            return val
        except ValueError:
            print("Invalid input, an integer must be entered")
        return False

    def get_ip_input(self):
        try:
            i = input("Enter an IP address: ")
            socket.inet_aton(i)
            return(i)
        except socket.error:
            print(f"IP address {i} is invalid")
            return False


    def set_port(self):
        while not (port := self.get_int_input("Enter new port number: ")):
            if (port > 2**16 -1):
                print("Port number is invalid")
                continue
        self.port = port
        self.wst.set_port(port)

    def set_ip(self):
        while not (ip := self.get_ip_input()):
            continue
        self.ip = ip
        self.wst.set_address(ip)
    
if __name__ == "__main__":
    menu = WSController(debug=True)
    menu.menu_loop()
