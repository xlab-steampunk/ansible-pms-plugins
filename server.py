# Copyright (c) 2019 XLAB d.o.o.

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time


class Handler(BaseHTTPRequestHandler):
    def _respond(self, status, body=None, headers=None):
        self.send_response(status)
        if body:
            self.send_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(json.dumps(body).encode("utf-8"))
        time.sleep(0.5)

    def do_GET(self):
        if not self.path.startswith("/test"):
            self._respond(404, dict(error="missing resource"))
        elif self.headers.get("x-auth-token") == "123":
            self._respond(200, dict(hello="world"))
        else:
            self._respond(403, dict(error="bad auth"))

    def do_POST(self):
        if self.path.rstrip("/") != "/tokens":
            return self._respond(404, dict(error="missing resource"))

        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        username = data.get("username")
        if username == "user" and data.get("password") == "pass":
            return self._respond(
                201, dict(username=username), {"x-auth-token": "123"},
            )

        self._respond(400, dict(error="bad auth"))

    def do_DELETE(self):
        if self.path.rstrip("/") != "/tokens/123":
            self._respond(404, dict(error="missing resource"))
        elif self.headers.get("x-auth-token") == "123":
            self._respond(204)
        else:
            self._respond(403, dict(error="bad auth"))


if __name__ == "__main__":
    address = "localhost", 8000
    print("Starting server on {}:{}".format(*address))

    server = HTTPServer(address, Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Closing server")
    server.server_close()
