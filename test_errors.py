"""Self-check for door errors. Run it with: python test_errors.py"""

import http.server
import threading

from gandr_mcp import server


def door(status, body, content_type="application/json"):
    """Start a local door that answers every request with one status."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def answer(self):
            self.send_response(status)
            self.send_header("content-type", content_type)
            self.end_headers()
            self.wfile.write(body)

        do_GET = do_POST = answer

        def log_message(self, *args):
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, args=(0.05,), daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_port}"


def against(status, body, *content_type):
    httpd, server.DOOR = door(status, body, *content_type)
    try:
        return server.synthesize("hello"), server.get_usage()
    finally:
        httpd.shutdown()
        httpd.server_close()


def main() -> None:
    server.KEY = "gnd_test"

    for got in against(402, b'{"error": "quota_exceeded", "hint": "upgrade at https://gandr.ai"}'):
        assert got == "error: [402] quota_exceeded, upgrade at https://gandr.ai", got

    for got in against(401, b'{"error": "invalid_api_key"}'):
        assert got == "error: [401] invalid_api_key", got

    for got in against(502, b"<html>Bad Gateway</html>", "text/html"):
        assert got == "error: HTTP Error 502: Bad Gateway", got

    print("ok: the door's JSON error reaches the agent, non-JSON keeps the status line")


if __name__ == "__main__":
    main()
