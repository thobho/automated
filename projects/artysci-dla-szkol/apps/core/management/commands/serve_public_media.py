"""Serve the public media directory on its own origin (filesystem backend, local use).

This is what makes `MEDIA_PUBLIC_BASE_URL` (e.g. http://pirx:8101) a different origin from the
app. Files are served inert: `nosniff`, a sandboxing CSP, no directory listings. Production
puts a real web server or CDN in front of the same directory/bucket.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from django.conf import settings
from django.core.management.base import BaseCommand


class PublicMediaHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "sandbox; default-src 'none'")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404, "Not found")
        return None


def make_server(root, host: str, port: int) -> ThreadingHTTPServer:
    handler = partial(PublicMediaHandler, directory=str(root))
    return ThreadingHTTPServer((host, port), handler)


class Command(BaseCommand):
    help = "Serve MEDIA_PUBLIC_ROOT on a separate port (the public media origin)."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=8101)

    def handle(self, *args, **options):
        root = settings.MEDIA_PUBLIC_ROOT
        root.mkdir(parents=True, exist_ok=True)
        server = make_server(root, options["host"], options["port"])
        self.stdout.write(f"Serving {root} on http://{options['host']}:{options['port']}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
