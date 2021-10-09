#!/usr/bin/env python3

from WebServer import WebServerThread
from xml.etree import ElementTree as ET

class WSController():
    def __init__(self, debug = False):
        self.debug = debug
        self.init_webserver_thread()
        self.generate_menu()

    def init_webserver_thread(self):
        if self.debug:
            print("Initializing webserver thread object")
        self.wst = WebServerThread(debug = self.debug)

    def generate_menu(self):
        menu = {}
        menu['1'] = ["Start Webserver", self.wst.start_webserver]
        menu['2'] = ["Stop Webserver", self.wst.stop]
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
        

if __name__ == "__main__":
    menu = WSController(debug=True)
    menu.menu_loop()
