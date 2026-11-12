import signal
import threading

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Background worker placeholder: idles until SIGINT/SIGTERM (job queue arrives in T05)."

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=float, default=30.0, help="Heartbeat seconds.")
        parser.add_argument("--once", action="store_true", help="Exit after one heartbeat.")

    def handle(self, *args, **options):
        stop = threading.Event()
        if threading.current_thread() is threading.main_thread():
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, lambda *_: stop.set())
        self.stdout.write("worker: started (no job queue yet)")
        while not stop.is_set():
            self.stdout.write("worker: idle")
            if options["once"]:
                break
            stop.wait(options["interval"])
        self.stdout.write("worker: stopped")
