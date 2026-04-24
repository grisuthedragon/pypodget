import os
from unittest.mock import patch, MagicMock
import pytest

import pypodget.globals as g
from pypodget.download import pod_download


@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"fake-audio-data"
    resp.headers = {"Content-Length": "1024"}
    resp.iter_content = (
        lambda chunk_size=1024: iter(
            [b"fake-audio-data"[:chunk_size]]
        )
    )
    return resp


@pytest.fixture
def mock_response_no_content_length():
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"fake-audio-data"
    resp.headers = {}
    resp.iter_content = (
        lambda chunk_size=1024: iter(
            [b"fake-audio-data"[:chunk_size]]
        )
    )
    return resp


def test_pod_download_verbose_writes_file(mock_response, tmp_path):
    g.set_verbose(True)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response,
    ):
        with patch(
            "pypodget.download.tqdm.tqdm",
            side_effect=lambda *a, **kw: iter([b"chunk"]),
        ):
            pod_download(
                "https://example.com/file.mp3", filepath
            )
    assert os.path.exists(filepath)


def test_pod_download_silent_writes_file(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch("pypodget.download.requests.get", return_value=mock_response):
        pod_download("https://example.com/file.mp3", filepath)
    assert os.path.exists(filepath)
    with open(filepath, "rb") as f:
        assert f.read() == b"fake-audio-data"


def test_pod_download_verbose_no_content_length(
    mock_response_no_content_length, tmp_path,
):
    g.set_verbose(True)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response_no_content_length,
    ):
        with patch(
            "pypodget.download.tqdm.tqdm",
            side_effect=lambda *a, **kw: iter([b"chunk"]),
        ):
            pod_download(
                "https://example.com/file.mp3", filepath
            )
    assert os.path.exists(filepath)


def test_pod_download_silent_no_content_length_needed(
    mock_response_no_content_length, tmp_path,
):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response_no_content_length,
    ):
        pod_download(
            "https://example.com/file.mp3", filepath
        )
    assert os.path.exists(filepath)


def test_pod_download_stream_depends_on_verbose(
    mock_response, tmp_path,
):
    g.set_verbose(True)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response,
    ) as mock_get:
        with patch(
            "pypodget.download.tqdm.tqdm",
            side_effect=lambda *a, **kw: iter([b"chunk"]),
        ):
            pod_download(
                "https://example.com/file.mp3", filepath
            )
        _, kwargs = mock_get.call_args
        assert kwargs["stream"] is True

    g.set_verbose(False)
    filepath2 = os.path.join(str(tmp_path), "test2.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response,
    ) as mock_get2:
        pod_download("https://example.com/file.mp3", filepath2)
        _, kwargs = mock_get2.call_args
        assert kwargs["stream"] is False


def test_pod_download_keyboard_interrupt_cleanup(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch("pypodget.download.requests.get", return_value=mock_response):
        with patch("builtins.open", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                pod_download("https://example.com/file.mp3", filepath)


def test_pod_download_keyboard_interrupt_removes_file(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch("pypodget.download.requests.get", return_value=mock_response):
        with patch("builtins.open", side_effect=KeyboardInterrupt):
            with patch("pypodget.download.os.path.exists", return_value=True):
                with patch("pypodget.download.os.remove") as mock_remove:
                    with pytest.raises(KeyboardInterrupt):
                        pod_download("https://example.com/file.mp3", filepath)
                    mock_remove.assert_called_once_with(filepath)


def test_pod_download_silent_uses_with_statement(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch("pypodget.download.requests.get", return_value=mock_response):
        pod_download("https://example.com/file.mp3", filepath)
    with open(filepath, "rb") as f:
        content = f.read()
    assert content == b"fake-audio-data"


def test_pod_download_filename_extraction(mock_response, tmp_path):
    g.set_verbose(True)
    filepath = os.path.join(
        str(tmp_path), "subdir", "test.mp3"
    )
    os.makedirs(
        os.path.join(str(tmp_path), "subdir"), exist_ok=True
    )
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response,
    ):
        with patch(
            "pypodget.download.tqdm.tqdm",
            side_effect=lambda *a, **kw: iter(
                [b"chunk"]
            ),
        ) as mock_tqdm:
            pod_download("https://example.com/file.mp3", filepath)
            call_kwargs = mock_tqdm.call_args[1] if mock_tqdm.call_args else {}
            assert call_kwargs.get("desc") == "test.mp3"


def test_pod_download_returns_none(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch("pypodget.download.requests.get", return_value=mock_response):
        result = pod_download("https://example.com/file.mp3", filepath)
    assert result is None


def test_pod_download_allow_redirects(mock_response, tmp_path):
    g.set_verbose(False)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    with patch(
        "pypodget.download.requests.get",
        return_value=mock_response,
    ) as mock_get:
        pod_download("https://example.com/file.mp3", filepath)
        _, kwargs = mock_get.call_args
        assert kwargs["allow_redirects"] is True


def test_pod_download_verbose_chunk_iteration(tmp_path):
    g.set_verbose(True)
    filepath = os.path.join(str(tmp_path), "test.mp3")
    chunks = [b"chunk1_", b"chunk2_", b"chunk3_"]
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"Content-Length": "3072"}
    resp.iter_content = lambda chunk_size=1024: iter(chunks)
    with patch(
        "pypodget.download.requests.get",
        return_value=resp,
    ):
        with patch(
            "pypodget.download.tqdm.tqdm",
            side_effect=lambda *a, **kw: iter(chunks),
        ):
            pod_download("https://example.com/file.mp3", filepath)
    with open(filepath, "rb") as f:
        assert f.read() == b"chunk1_chunk2_chunk3_"
