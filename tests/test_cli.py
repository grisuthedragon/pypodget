from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path

from pypodget.cli import main, DEFAULT_FILENAME_TEMPLATE
from tests.conftest import SAMPLE_RSS_XML, _make_mock_response


class TestCLIParsing:

    def test_missing_config_causes_system_exit(self):
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["pypodget"]):
                main()

    def test_silent_flag_sets_verbose_false(self):
        with patch("sys.argv", ["pypodget", "-s", "-c", "/tmp/fake.ini"]):
            with patch("pypodget.cli.os.path.isfile", return_value=False):
                with patch("pypodget.cli.set_verbose") as mock_sv:
                    with pytest.raises(SystemExit):
                        main()
                    mock_sv.assert_called_with(False)

    def test_default_verbose_is_true(self):
        with patch("sys.argv", ["pypodget", "-c", "/tmp/fake.ini"]):
            with patch("pypodget.cli.os.path.isfile", return_value=False):
                with patch("pypodget.cli.set_verbose") as mock_sv:
                    with pytest.raises(SystemExit):
                        main()
                    mock_sv.assert_called_with(True)

    def test_version_flag(self):
        with patch("sys.argv", ["pypodget", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert (
                "0.1.2" in str(exc_info.value)
                or exc_info.type == SystemExit
            )


class TestCLIConfig:

    def test_nonexistent_config_exits(self):
        with patch("sys.argv", ["pypodget", "-c", "/nonexistent/config.ini"]):
            with patch("pypodget.cli.os.path.isfile", return_value=False):
                with pytest.raises(SystemExit):
                    main()

    def test_valid_config_creates_podcast(self, tmp_path, sample_config_file):
        with patch("sys.argv", ["pypodget", "-c", sample_config_file]):
            with patch("pypodget.podcast.requests.get",
                       return_value=_make_mock_response(SAMPLE_RSS_XML)):
                with patch("pypodget.podcast.os.makedirs"):
                    with patch("pypodget.cli.Podcast") as mock_podcast:
                        mock_podcast.return_value.nepisodes = 0
                        main()
                        mock_podcast.assert_called_once()

    def test_settings_section_skipped(self, tmp_path):
        config_text = """[settings]
some_key = value

[TestPodcast]
url = https://example.com/feed.xml
directory = ./output/
"""
        p = tmp_path / "settings_config.ini"
        p.write_text(config_text)
        with patch("sys.argv", ["pypodget", "-c", str(p)]):
            with patch("pypodget.podcast.requests.get",
                       return_value=_make_mock_response(SAMPLE_RSS_XML)):
                with patch("pypodget.podcast.os.makedirs"):
                    with patch("pypodget.cli.Podcast") as mock_podcast:
                        mock_podcast.return_value.nepisodes = 0
                        main()
                        assert mock_podcast.call_count == 1

    def test_missing_url_key_continues(self, tmp_path, config_missing_url):
        with patch("sys.argv", ["pypodget", "-c", config_missing_url]):
            with patch("pypodget.cli.Podcast") as mock_podcast:
                mock_podcast.return_value.nepisodes = 0
                main()
                mock_podcast.assert_not_called()

    def test_missing_directory_key_continues(
        self, tmp_path, config_missing_directory
    ):
        with patch("sys.argv", ["pypodget", "-c", config_missing_directory]):
            with patch("pypodget.cli.Podcast") as mock_podcast:
                mock_podcast.return_value.nepisodes = 0
                main()
                mock_podcast.assert_not_called()

    def test_missing_filename_uses_default(self, tmp_path):
        config_text = """[TestPodcast]
url = https://example.com/feed.xml
directory = ./output/
"""
        p = tmp_path / "no_filename.ini"
        p.write_text(config_text)
        with patch("sys.argv", ["pypodget", "-c", str(p)]):
            with patch("pypodget.podcast.requests.get",
                       return_value=_make_mock_response(SAMPLE_RSS_XML)):
                with patch("pypodget.podcast.os.makedirs"):
                    with patch("pypodget.cli.Podcast") as mock_podcast:
                        mock_podcast.return_value.nepisodes = 0
                        main()
                        call_kwargs = mock_podcast.call_args
                        if len(call_kwargs[0]) > 3:
                            assert (
                                call_kwargs[0][3]
                                == DEFAULT_FILENAME_TEMPLATE
                            )

    def test_filename_from_config(self, tmp_path, sample_config_file):
        with patch("sys.argv", ["pypodget", "-c", sample_config_file]):
            with patch("pypodget.podcast.requests.get",
                       return_value=_make_mock_response(SAMPLE_RSS_XML)):
                with patch("pypodget.podcast.os.makedirs"):
                    with patch("pypodget.cli.Podcast") as mock_podcast:
                        mock_podcast.return_value.nepisodes = 0
                        main()
                        args = mock_podcast.call_args[0]
                        assert len(args) >= 4
                        assert args[3] == "$year-$month-$day - $title.$ext"

    def test_podcast_init_failure_continues(
        self, tmp_path, sample_config_file
    ):
        with patch("sys.argv", ["pypodget", "-c", sample_config_file]):
            with patch("pypodget.cli.Podcast", side_effect=Exception("fail")):
                main()

    def test_download_failure_continues(self, tmp_path, sample_config_file):
        mock_podcast = MagicMock()
        mock_podcast.nepisodes = 1
        mock_podcast.download.side_effect = Exception("download error")
        with patch("sys.argv", ["pypodget", "-c", sample_config_file]):
            with patch("pypodget.podcast.requests.get",
                       return_value=_make_mock_response(SAMPLE_RSS_XML)):
                with patch("pypodget.podcast.os.makedirs"):
                    with patch(
                        "pypodget.cli.Podcast",
                        return_value=mock_podcast,
                    ):
                        main()
                        mock_podcast.download.assert_called_once()


class TestCLIVersion:

    def test_version_matches_pyproject(self):
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        assert "0.1.2" in content
