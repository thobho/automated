"""Tests for check_links.py. Run from this folder: python3 -m unittest"""

import http.server
import io
import os
import tempfile
import threading
import unittest
from contextlib import redirect_stdout

import check_links


class Handler(http.server.BaseHTTPRequestHandler):
    def _respond(self, body):
        path = self.path
        if path == "/ok":
            code = 200
        elif path == "/redirect":
            self.send_response(301)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        elif path == "/gone":
            code = 410
        elif path == "/forbidden":
            code = 403
        elif path == "/ratelimit":
            code = 429
        elif path == "/error":
            code = 500
        elif path == "/nohead":
            code = 405 if self.command == "HEAD" else 200
        elif path == "/slow":
            threading.Event().wait(2)
            code = 200
        else:
            code = 404
        self.send_response(code)
        self.send_header("Content-Length", "2")
        self.end_headers()
        if body:
            self.wfile.write(b"ok")

    def do_HEAD(self):
        self._respond(False)

    def do_GET(self):
        self._respond(True)

    def log_message(self, *args):
        pass


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def check(self, path, timeout=5):
        return check_links.check_url(self.base + path, timeout=timeout)[0]

    def test_ok(self):
        self.assertEqual(self.check("/ok"), "ok")

    def test_redirect_followed(self):
        self.assertEqual(self.check("/redirect"), "ok")

    def test_404_and_410_dead(self):
        self.assertEqual(self.check("/missing"), "dead")
        self.assertEqual(self.check("/gone"), "dead")

    def test_403_429_500_unverifiable(self):
        self.assertEqual(self.check("/forbidden"), "unverifiable")
        self.assertEqual(self.check("/ratelimit"), "unverifiable")
        self.assertEqual(self.check("/error"), "unverifiable")

    def test_head_rejected_falls_back_to_get(self):
        self.assertEqual(self.check("/nohead"), "ok")

    def test_timeout_unverifiable(self):
        self.assertEqual(self.check("/slow", timeout=0.5), "unverifiable")

    def test_dns_failure_dead(self):
        # .invalid is reserved (RFC 2606) and never resolves.
        result, detail = check_links.check_url("http://no-such-host.invalid/", 5)
        self.assertEqual(result, "dead", detail)

    def run_main(self, text, suffix=".md"):
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w") as f:
            f.write(text)
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                code = check_links.main([path, "--timeout", "5"])
        finally:
            os.remove(path)
        return code, out.getvalue()

    def test_main_exit_0_with_only_unverifiable(self):
        code, out = self.run_main("[a](%s/ok) and %s/forbidden." % (self.base, self.base))
        self.assertEqual(code, 0, out)
        self.assertIn("1 ok, 0 dead, 1 unverifiable", out)

    def test_main_exit_1_with_dead(self):
        code, out = self.run_main("see %s/ok, %s/missing" % (self.base, self.base))
        self.assertEqual(code, 1, out)
        self.assertIn("DEAD (1)", out)
        self.assertIn("/missing", out)

    def test_main_csv(self):
        code, out = self.run_main(
            "id,url\n1,%s/ok\n2,\"%s/gone\"\n" % (self.base, self.base), ".csv"
        )
        self.assertEqual(code, 1, out)
        self.assertIn("1 ok, 1 dead", out)


class ExtractTest(unittest.TestCase):
    def test_markdown_bare_and_dedupe(self):
        text = (
            "See [G2](https://www.g2.com/) and https://www.g2.com/.\n"
            "Bare https://example.com/a, then (https://example.com/b).\n"
            "<https://example.com/c> **https://example.com/d**\n"
            "| https://example.com/e | x |\n"
        )
        self.assertEqual(
            check_links.extract_urls(text),
            [
                "https://www.g2.com/",
                "https://example.com/a",
                "https://example.com/b",
                "https://example.com/c",
                "https://example.com/d",
                "https://example.com/e",
            ],
        )

    def test_balanced_parentheses_kept(self):
        text = "[w](https://en.wikipedia.org/wiki/Foo_(bar))"
        self.assertEqual(
            check_links.extract_urls(text), ["https://en.wikipedia.org/wiki/Foo_(bar)"]
        )

    def test_glued_csv_urls_split(self):
        self.assertEqual(
            check_links.extract_urls("https://a.example/x,https://b.example/y"),
            ["https://a.example/x", "https://b.example/y"],
        )


if __name__ == "__main__":
    unittest.main()
