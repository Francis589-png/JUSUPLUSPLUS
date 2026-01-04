import os
import sys
import threading
import http.server
import socketserver

# Ensure project root is on sys.path when running tests directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime.stdlib import get_builtins


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'hello jusu')

    def log_message(self, format, *args):
        # silence server logs during tests
        return


def _run_server(port, ready_event):
    with socketserver.TCPServer(('127.0.0.1', port), _Handler) as httpd:
        ready_event.set()
        httpd.handle_request()  # handle a single request then exit


def test_http_get_local_server():
    port = 8008
    ready = threading.Event()
    t = threading.Thread(target=_run_server, args=(port, ready), daemon=True)
    t.start()
    ready.wait(timeout=2)

    builtins = get_builtins()
    http = builtins['http']
    res = http.get(f'http://127.0.0.1:{port}/')
    assert res['status'] == 200
    assert 'hello' in res['text']
