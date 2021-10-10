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

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format%args))

    def log_error(self, format, *args):
        logging.error("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format%args))

from http.server import ThreadingHTTPServer
import socket
#Web server Class
class WebServer(ThreadingHTTPServer):
    def __init__(self, port = 8080, address = '127.0.0.tial1', request_handler = WebServerResponder, *args, **kwargs):
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
            return
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
        try:
            port = int(port)
            if port < 1:
                raise ValueError(f"Port ({port}) cannot be less than 1")
            if port < 1024:
                logging.warning(f"Port ({port}) is lower than 1024, additional permissions may be needed")
        except ValueError:
            raise ValueError(f"Specified port ({port}) is not an integer")
        logging.debug(f"Port has been set to {port}")
        self.port = port

    def set_address(self, address):
        try:
            socket.inet_aton(address)
            self.address = address
        except socket.error:
            raise socket.error(f"Address {address} is not a valid IP address")

    def start_webserver(self):
        #Creates new threaded webserver instance since old one is nuked when the thread is stopped
        try:
            try:
                if not isinstance(self.ws, WebServer):
                    self.init_webserver()
            except AttributeError:
                self.init_webserver()
        except PermissionError:
            raise PermissionError(f"Failed to bind to socket {self.address}:{self.port}")
        logging.debug(f"Thread status {self.is_alive()}")
        if self.is_alive():
            self.stop_event.clear()
            logging.info("Thread is already running")
        else:
            self.start()

    def kill(self):
        if not self.is_alive():
            logging.debug("Not killing thread as it has not been started")
        elif not hasattr(self, "ws"):
            logging.debug("Webserver object has not been initialied, not killing")
        else:
            logging.debug("Sending kill signal")
            self.kill_signal.set()
            self.stop()

    def stop(self):
        try:
            if not hasattr(self, "ws"):
                logging.info("Webserver object has not been initialized")
                return
            if not isinstance(self.ws, WebServer):
                logging.info("Webserver object is invalid")
                return
        except AttributeError:
            logging.debug("Webserver is not stopping because it has not been started")
            return
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
