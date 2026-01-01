import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from multi_etf_tracker import MultiETFTracker

PORT = int(os.getenv("PORT", "10000"))


def start_tracker():
    tracker = MultiETFTracker()
    tracker.run()


class HealthHandler(BaseHTTPRequestHandler):
    def _respond_ok(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        if self.path == "/health":
            self._respond_ok()
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        if self.path == "/health":
            # Uptime monitors often send HEAD; respond 200 to avoid false downs
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging to keep stdout clean
        return


def main():
    tracker_thread = threading.Thread(target=start_tracker, daemon=True)
    tracker_thread.start()

    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"Health server listening on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
