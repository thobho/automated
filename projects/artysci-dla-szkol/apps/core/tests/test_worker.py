from django.core.management import call_command


def test_worker_once_exits(capsys):
    call_command("worker", "--once")
    out = capsys.readouterr().out
    assert "started" in out
    assert "stopped" in out
