from threading import Thread, Event
from time import sleep
import logging
from http.server import BaseHTTPRequestHandler
#Webserver Responder Class
class WebServerResponder(BaseHTTPRequestHandler):
    content = [
            "<html>",
            "<body>",
            "<p>test</p>",
            "</body>",
            "</html>"
            ]

    def print_content(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.content)))
        self.end_headers()
        for line in self.content:
            self.wfile.write(line.encode("utf-8"))

    #Respond to get requests
    def do_GET(self):
        self.print_content() 

from http.server import ThreadingHTTPServer
import socket
#Web server Class
class WebServer(ThreadingHTTPServer):
    def __init__(self, port = 8080, address = '127.0.0.1', request_handler = WebServerResponder, *args, **kwargs):
        self.address = address
        self.port = port
        self.running = False
        kwargs['server_address'] = (address, port)
        kwargs['RequestHandlerClass'] = request_handler
        super(WebServer, self).__init__(*args, **kwargs)

    def serve(self):
        logging.info(f'Starting server on http://{self.address}:{self.port}')
        self.running = True
        self.serve_forever()
        self.server_close()
        self.running = False
        logging.info("Webserver has stoppped")
   
    def stop(self):
        if not self.running:
            logging.debug("Webserver is not running, not stopping")
            return False
        logging.info("Stopping webserver")
        self.shutdown()

class WebServerThread(Thread):
    def __init__(self, run_server = False, port = 8080, address = '127.0.0.1', *args, **kwargs):
        self.set_address(address)
        self.set_port(port)
        self.stop_event = Event()
        self.kill_signal = Event()
        Thread.__init__(self)
        if run_server:
            self.start_webserver()

    def init_webserver(self):
        self.ws = WebServer(port = self.port, address = self.address)

    def set_port(self, port):
        self.port = port

    def set_address(self, address):
        self.address = address

    def start_webserver(self):
        #Creates new threaded webserver instance since old one is nuked when the thread is stopped
        try:
            try:
                if not isinstance(self.ws, WebServer):
                    self.init_webserver()
            except AttributeError:
                self.init_webserver()
        except PermissionError:
            logging.error(f"Failed to bind to socket {self.address}:{self.port}")
            return False
        logging.debug(f"Thread status {self.is_alive()}")
        if self.is_alive():
            self.stop_event.clear()
            logging.debug("Thread is already running")
        else:
            self.start()

    def kill(self):
        logging.debug("Sending kill signal to thread")
        self.kill_signal.set()
        self.stop()

    def stop(self):
        logging.debug("Preparing to stop webserver")
        self.stop_event.set()
        if self.stop_event.is_set():
            logging.debug("Thread stop signal has been set")
        if self.ws.stop():
            logging.info("Webserver has stopped")
        #delete the object so a fresh one will be made when server is restarted
        del self.ws
        logging.debug("Webserver has been deleted")

    def run(self):
        while True:
            if self.kill_signal.is_set():
                logging.debug("Kill signal received, ending thread")
                break
            if self.stop_event.is_set():
                sleep(1)
                logging.debug("Waiting to restart webserver")
                continue
            logging.debug(f'Starting webserver thread')
            self.ws.serve()
