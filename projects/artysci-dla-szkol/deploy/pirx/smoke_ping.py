"""Smoke test for the job path: defer a `core.ping` job and wait until the worker ran it.

Run through the Django shell so settings are loaded:
    uv run python manage.py shell -c "exec(open('deploy/pirx/smoke_ping.py').read())"
Exit code 1 if the worker did not process the job in time.
"""

import sys
import time
import uuid

from apps.core.jobs import enqueue
from apps.core.models import PingRecord
from apps.core.tasks import ping

token = f"smoke-{uuid.uuid4().hex[:12]}"
enqueue(ping, token=token)
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    if PingRecord.objects.filter(token=token).exists():
        print(f"ping job ran: {token}")
        break
    time.sleep(1)
else:
    print(f"FAIL: ping job {token} not processed in 30s (is ads-worker running?)")
    sys.exit(1)
