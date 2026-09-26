import datetime
import http.server
import socketserver
import urllib.parse

PAGE = "/tmp/e6-page.html"
LOG = "/tmp/e6t-traj.log"
PORT = 8767


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 5

    def log_message(self, *args):
        pass

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/traj":
            q = urllib.parse.parse_qs(u.query)
            d = (q.get("d") or [""])[0]
            with open(LOG, "a") as f:
                f.write("%s\t%s\n" % (
                    datetime.datetime.now().isoformat(timespec="seconds"), d))
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if u.path in ("/", "/e6-page.html"):
            with open(PAGE, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("127.0.0.1", PORT), Handler) as srv:
    srv.serve_forever()
