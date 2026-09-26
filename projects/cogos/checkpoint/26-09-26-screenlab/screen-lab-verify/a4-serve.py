import datetime
import http.server
import socketserver
import urllib.parse

PAGE = "/tmp/a4-page.html"
HITS = "/tmp/a4-hits.log"
REQ = "/tmp/a4-requests.log"
PORT = 8765


ACCEPTS = "/tmp/a4-accepts.log"


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 5

    def setup(self):
        try:
            with open(ACCEPTS, "a") as f:
                f.write("%s accept %s\n" % (
                    datetime.datetime.now().isoformat(timespec="milliseconds"),
                    self.client_address))
        except Exception:
            pass
        super().setup()

    def log_message(self, *args):
        pass

    def _log(self, line):
        with open(REQ, "a") as f:
            f.write(line + "\n")

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        self._log("%s %s" % (
            datetime.datetime.now().isoformat(timespec="milliseconds"), self.path))
        if u.path == "/hit":
            q = urllib.parse.parse_qs(u.query)
            name = (q.get("c") or ["?"])[0]
            with open(HITS, "a") as f:
                f.write("%s %s\n" % (
                    datetime.datetime.now().isoformat(timespec="milliseconds"), name))
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if u.path in ("/", "/index.html"):
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
