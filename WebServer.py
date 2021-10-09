from threading import Thread, Event
from time import sleep

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
#Web server Class
class WebServer(ThreadingHTTPServer):
    def __init__(self, debug = False, port = 8080, address = '127.0.0.1', request_handler = WebServerResponder, *args, **kwargs):
        self.debug = debug
        self.set_port(port)
        self.set_address(address)
        self.running = False
        kwargs['server_address'] = (address, port)
        kwargs['RequestHandlerClass'] = request_handler
        super(WebServer, self).__init__(*args, **kwargs)

    def set_address(self, address):
        self.address = address

    def set_port(self, port):
        try:
            port = int(port)
        except ValueError:
            return False
        if port < (2**16 -1):
            self.port = port
            return True
        return False
    
    def serve(self):
        if self.debug:
            print(f'Starting server on http://{self.address}:{self.port}')
        self.running = True
        self.serve_forever()
        self.server_close()
        self.running = False
        if self.debug:
            print("Webserver has stoppped")
   
    def stop(self):
        if not self.running:
            if self.debug:
                print("Webserver is not running, not stopping")
            return False
        if self.debug:
            print("Stopping webserver")
        self.shutdown()

class WebServerThread(Thread):
    def __init__(self, run_server = False, debug = False, *args, **kwargs):
        self.debug = debug
        self.init_webserver()
        self.stop_event = Event()
        self.kill_signal = Event()
        Thread.__init__(self)
        if run_server:
            self.start_webserver()

    def init_webserver(self):
        self.ws = WebServer(debug = self.debug)

    def start_webserver(self):
        #Creates new threaded webserver instance since old one is nuked when the thread is stopped
        try:
            if not isinstance(self.ws, WebServer):
                self.init_webserver()
        except AttributeError:
            self.init_webserver()
        if self.debug:
            print(f"Thread status {self.is_alive()}")
        if self.is_alive():
            self.stop_event.clear()
            if self.debug:
                print("Thread is already running")
        else:
            self.start()

    def kill(self):
        if self.debug:
            print("Sending kill signal to thread")
        self.kill_signal.set()
        self.stop()

    def stop(self):
        if self.debug:
            print("Preparing to stop webserver")
        self.stop_event.set()
        if self.stop_event.is_set() and self.debug:
            print("Thread stop signal has been set")
        if self.ws.stop() and self.debug:
            print("Webserver has stopped")
        #delete the object so a fresh one will be made when server is restarted
        del self.ws
        if self.debug:
            print("Webserver has been deleted")

    def run(self):
        while True:
            if self.kill_signal.is_set():
                print("Kill signal received, ending thread")
                break
            if self.stop_event.is_set():
                sleep(1)
                if self.debug:
                    print("Waiting to restart webserver")
                continue
            if self.debug:
                print(f'Starting webserver thread')
            self.ws.serve()
