import threading
import urllib.error
import urllib.request

import pytest
from django.core.management import call_command

from apps.core.management.commands.serve_public_media import make_server
from config.settings.storage import build_storages


@pytest.fixture
def served(tmp_path):
    (tmp_path / "photo").mkdir()
    (tmp_path / "photo" / "a.jpg").write_bytes(b"\xff\xd8\xff data")
    server = make_server(tmp_path, "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_public_origin_serves_files_inert(served):
    with urllib.request.urlopen(f"{served}/photo/a.jpg", timeout=5) as resp:  # noqa: S310
        assert resp.status == 200
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert "sandbox" in resp.headers["Content-Security-Policy"]


def test_public_origin_has_no_directory_listing(served):
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(f"{served}/photo/", timeout=5)  # noqa: S310
    assert err.value.code == 404


def test_ensure_buckets_is_a_noop_on_filesystem(settings, capsys):
    settings.STORAGE_BACKEND = "filesystem"
    call_command("ensure_buckets")
    assert "nothing to do" in capsys.readouterr().out


def test_build_storages_s3_shapes_public_origin(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://minio:9000")
    cfg = build_storages(
        "s3", public_base_url="http://pirx:19000/public/", private_root="/x", public_root="/y"
    )
    assert cfg["private"]["OPTIONS"]["querystring_auth"] is True
    assert cfg["public"]["OPTIONS"]["querystring_auth"] is False
    assert cfg["public"]["OPTIONS"]["custom_domain"] == "pirx:19000/public"
    assert cfg["public"]["OPTIONS"]["url_protocol"] == "http:"


def test_build_storages_filesystem_public_base_url():
    cfg = build_storages(
        "filesystem", public_base_url="http://pirx:8101", private_root="/p", public_root="/q"
    )
    assert cfg["public"]["OPTIONS"]["base_url"] == "http://pirx:8101/"
    assert cfg["private"]["OPTIONS"]["location"] == "/p"


def test_build_storages_rejects_unknown_backend():
    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured):
        build_storages("ftp", public_base_url="x", private_root="/p", public_root="/q")
