#!/usr/bin/env python3

from WebServer import WebServerThread
from xml.etree import ElementTree as ET
import socket
import logging

class WSController():
    def __init__(self):
        self.init_webserver_thread()
        self.generate_menu()

    def init_webserver_thread(self):
        logging.debug("Initializing webserver thread object")
        self.wst = WebServerThread()
        if hasattr(self, "port"):
            self.wst.set_port(self.port)
        if hasattr(self, "ip"):
            self.wst.set_address(self.ip)

    def generate_menu(self):
        menu = {}
        menu['r'] = ["Start Webserver", self.wst.start_webserver]
        menu['s'] = ["Stop Webserver", self.wst.stop]
        menu['k'] = ["Kill thread", self.wst.kill]
        menu['p'] = ["Set port", self.set_port]
        menu['i'] = ["Set IP", self.set_ip]
        menu['d'] = ["Change debug level", self.set_debug]
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
            logging.error("Invalid choice")
            return None
    
    def process_choice(self, choice):
        logging.debug(f"Selected choice:{choice} mapped function:{self.menu[choice][1]}")
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
            logging.error("Invalid input, an integer must be entered")
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
                logging.error("Port number is invalid")
                continue
        self.port = port
        self.wst.set_port(port)

    def set_ip(self):
        while not (ip := self.get_ip_input()):
            continue
        self.ip = ip
        self.wst.set_address(ip)

    def set_debug(self):
        print("Levels: 0 - 50")
        print("Critical - 50")
        print("Error - 40")
        print("Warning - 30")
        print("Info - 20")
        print("Debug - 10")
        while not(level := self.get_int_input("Enter desired logging level: ")):
            if (level > 50):
                logging.error("Level is invalid")
                continue
        logging.debug(f"Setting log level to {level}")
        logging.getLogger().setLevel(level)
    
if __name__ == "__main__":
    menu = WSController()
    menu.menu_loop()
