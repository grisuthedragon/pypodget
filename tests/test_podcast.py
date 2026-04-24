import os
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest

from pypodget.podcast import Podcast, Episode

from tests.conftest import (
    SAMPLE_RSS_XML, RSS_NO_DESCRIPTION, RSS_NO_LINK, RSS_NO_IMAGE,
    RSS_NO_ENCLOSURE, RSS_ITEM_NO_LINK, RSS_EMPTY_ITEMS,
    _make_mock_response,
)


def _mock_podcast(rss_xml, folder=".", title="TestPodcast",
                  filename_template="$year-$month-$day - $title.$ext"):
    with patch("pypodget.podcast.requests.get",
               return_value=_make_mock_response(rss_xml)):
        with patch("pypodget.podcast.os.makedirs"):
            p = Podcast(url="https://example.com/feed.xml",
                        mytitle=title,
                        folder=folder,
                        filename_template=filename_template)
    return p


class TestEpisode:

    def _make_episode(self, url="https://example.com/ep.mp3",
                      local_filename="/tmp/test.mp3"):
        parent = MagicMock()
        parent.title = "Test Podcast"
        epi = Episode(
            parent=parent,
            title="Test Episode",
            description="A test",
            pubdate=datetime(2022, 1, 31, 18, 43),
            url=url,
            link="https://example.com/ep",
            local_filename=local_filename,
        )
        return epi

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_download_calls_pod_download(
        self, mock_eyed3, mock_isfile, mock_dl
    ):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode()
        epi.download()
        mock_dl.assert_called_once_with(
            "https://example.com/ep.mp3", "/tmp/test.mp3"
        )

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=True)
    @patch("pypodget.podcast.eyed3")
    def test_download_skips_existing_file(
        self, mock_eyed3, mock_isfile, mock_dl
    ):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode()
        epi.download()
        mock_dl.assert_not_called()

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_download_skips_none_url(self, mock_eyed3, mock_isfile, mock_dl):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode(url=None)
        epi.download()
        mock_dl.assert_not_called()

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_id3_sets_artist_when_empty(
        self, mock_eyed3, mock_isfile, mock_dl
    ):
        mock_eyed3.load.return_value.tag.artist = None
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode()
        epi.download()
        assert mock_eyed3.load.return_value.tag.artist == "Test Podcast"

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_id3_sets_title_when_empty(self, mock_eyed3, mock_isfile, mock_dl):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = None
        epi = self._make_episode()
        epi.download()
        assert mock_eyed3.load.return_value.tag.title == "Test Episode"

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_id3_preserves_existing_tags(
        self, mock_eyed3, mock_isfile, mock_dl
    ):
        mock_eyed3.load.return_value.tag.artist = "Existing Artist"
        mock_eyed3.load.return_value.tag.title = "Existing Title"
        epi = self._make_episode()
        epi.download()
        assert mock_eyed3.load.return_value.tag.artist == "Existing Artist"
        assert mock_eyed3.load.return_value.tag.title == "Existing Title"

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_id3_tag_save_called(self, mock_eyed3, mock_isfile, mock_dl):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode()
        epi.download()
        mock_eyed3.load.return_value.tag.save.assert_called()

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_id3_tag_none_handled(self, mock_eyed3, mock_isfile, mock_dl):
        mock_audiofile = MagicMock()
        mock_audiofile.tag = None
        mock_eyed3.load.return_value = mock_audiofile
        mock_eyed3.log.setLevel = MagicMock()

        def fake_init_tag():
            mock_audiofile.tag = MagicMock()
            mock_audiofile.tag.artist = None
            mock_audiofile.tag.title = None
        mock_audiofile.initTag = fake_init_tag

        epi = self._make_episode()
        epi.download()
        assert mock_audiofile.tag is not None

    @patch("pypodget.podcast.pod_download")
    @patch("pypodget.podcast.os.path.isfile", return_value=False)
    @patch("pypodget.podcast.eyed3")
    def test_eyed3_log_level(self, mock_eyed3, mock_isfile, mock_dl):
        mock_eyed3.load.return_value.tag.artist = "Artist"
        mock_eyed3.load.return_value.tag.title = "Title"
        epi = self._make_episode()
        epi.download()
        mock_eyed3.log.setLevel.assert_called_with("ERROR")


class TestPodcastConstruction:

    def test_init_calls_update(self):
        with patch(
            "pypodget.podcast.requests.get",
            return_value=_make_mock_response(SAMPLE_RSS_XML),
        ) as mock_get:
            with patch("pypodget.podcast.os.makedirs"):
                Podcast(url="https://example.com/feed.xml",
                        mytitle="Test", folder=".")
                assert mock_get.call_count >= 1

    def test_init_creates_folder(self, tmp_path):
        folder = os.path.join(str(tmp_path), "test_folder")
        with patch("pypodget.podcast.requests.get",
                   return_value=_make_mock_response(SAMPLE_RSS_XML)):
            with patch("pypodget.podcast.os.makedirs") as mock_mkdir:
                Podcast(url="https://example.com/feed.xml",
                        mytitle="Test", folder=folder)
                mock_mkdir.assert_called()

    def test_non_200_status_raises(self):
        resp = MagicMock()
        resp.status_code = 404
        resp.content = b""
        with patch("pypodget.podcast.requests.get", return_value=resp):
            with patch("pypodget.podcast.os.makedirs"):
                with pytest.raises(Exception, match="return code 404"):
                    Podcast(url="https://example.com/404",
                            mytitle="Test", folder=".")

    def test_title_from_feed(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.title == "Test Podcast"

    def test_description_from_feed(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.description == "A test podcast feed"

    def test_link_from_feed(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.link == "https://example.com/"

    def test_image_from_feed(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.image == "https://example.com/image.png"

    def test_nepisodes(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.nepisodes == 2

    def test_episode_returns_episode(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        epi = p.episode(0)
        assert epi is not None

    def test_episode_out_of_range(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.episode(999) is None

    def test_episode_negative(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.episode(-1) is None

    def test_url_property(self):
        p = _mock_podcast(SAMPLE_RSS_XML)
        assert p.url == "https://example.com/feed.xml"

    def test_folder_property(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp/test_pod")
        assert p.folder == "/tmp/test_pod"

    def test_filename_template_property(self):
        p = _mock_podcast(SAMPLE_RSS_XML,
                          filename_template="$mytitle - $title.$ext")
        assert p.filename_template == "$mytitle - $title.$ext"

    def test_mytitle_property(self):
        p = _mock_podcast(SAMPLE_RSS_XML, title="MyPodcast")
        assert p.mytitle == "MyPodcast"


class TestPodcastDownload:

    @patch("pypodget.podcast.pod_download")
    def test_download_specific_episode(self, mock_dl):
        p = _mock_podcast(SAMPLE_RSS_XML)
        epi = p.episode(0)
        with patch.object(epi, "download") as mock_epi_dl:
            p.download(0)
            mock_epi_dl.assert_called_once()

    @patch("pypodget.podcast.pod_download")
    def test_downloadall(self, mock_dl):
        p = _mock_podcast(SAMPLE_RSS_XML)
        episodes = [p.episode(i) for i in range(p.nepisodes)]
        with patch.object(episodes[0], "download") as mock_dl0, \
             patch.object(episodes[1], "download") as mock_dl1:
            p.downloadall()
            mock_dl0.assert_called_once()
            mock_dl1.assert_called_once()


class TestFilenameTemplating:

    def test_default_template(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        assert epi is not None
        assert (
            "/tmp" in epi._Episode__local_filename
            or "/tmp" in epi._Episode__local_filename
        )

    def test_custom_template_with_mytitle(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp",
                          filename_template="$mytitle - $title.$ext")
        epi = p.episode(0)
        assert "TestPodcast" in epi._Episode__local_filename

    def test_sanitization_backslash(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert "\\" not in filename.split(os.sep)[-1]

    def test_sanitization_slash(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert "/" not in filename.split(os.sep)[-1]

    def test_sanitization_colon(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert ":" not in filename.split(os.sep)[-1]

    def test_sanitization_question_mark(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert "?" not in filename.split(os.sep)[-1]

    def test_sanitization_asterisk(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert "*" not in filename.split(os.sep)[-1]

    def test_sanitization_angle_brackets(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        basename = filename.split(os.sep)[-1]
        assert ">" not in basename
        assert "<" not in basename

    def test_sanitization_pipe(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert "|" not in filename.split(os.sep)[-1]

    def test_extension_extraction_mp3(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert filename.endswith(".mp3")

    def test_extension_extraction_with_query_params(self):
        rss = SAMPLE_RSS_XML.replace(
            'url="https://example.com/ep1.mp3"',
            'url="https://example.com/ep1.mp3?token=abc"'
        )
        p = _mock_podcast(rss, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        assert filename.endswith(".mp3")

    def test_title_quote_removal(self):
        rss = SAMPLE_RSS_XML.replace(
            "<title>Episode One</title>",
            '<title>Episode "One\'s Test</title>'
        )
        p = _mock_podcast(rss, folder="/tmp")
        epi = p.episode(0)
        filename = epi._Episode__local_filename
        basename = filename.split(os.sep)[-1]
        assert '"' not in basename
        assert "'" not in basename


class TestEdgeCases:

    def test_missing_description(self):
        p = _mock_podcast(RSS_NO_DESCRIPTION)
        assert p.description is None

    def test_missing_channel_link(self):
        p = _mock_podcast(RSS_NO_LINK)
        assert p.link is None

    def test_missing_image(self):
        p = _mock_podcast(RSS_NO_IMAGE)
        assert p.image is None

    def test_missing_enclosure_ext_defaults(self):
        p = _mock_podcast(RSS_NO_ENCLOSURE, folder="/tmp")
        epi = p.episode(0)
        assert epi is not None
        assert epi._Episode__url is None

    def test_item_no_link_defaults_empty(self):
        p = _mock_podcast(RSS_ITEM_NO_LINK, folder="/tmp")
        epi = p.episode(0)
        assert epi is not None

    def test_folder_setter_triggers_update(self):
        with patch(
            "pypodget.podcast.requests.get",
            return_value=_make_mock_response(SAMPLE_RSS_XML),
        ) as mock_get:
            with patch("pypodget.podcast.os.makedirs"):
                p = Podcast(url="https://example.com/feed.xml",
                            mytitle="Test", folder=".")
                initial_calls = mock_get.call_count
                p.folder = "./new_folder"
                assert mock_get.call_count > initial_calls

    def test_filename_template_setter_triggers_update(self):
        with patch(
            "pypodget.podcast.requests.get",
            return_value=_make_mock_response(SAMPLE_RSS_XML),
        ) as mock_get:
            with patch("pypodget.podcast.os.makedirs"):
                p = Podcast(url="https://example.com/feed.xml",
                            mytitle="Test", folder=".")
                initial_calls = mock_get.call_count
                p.filename_template = "$title.$ext"
                assert mock_get.call_count > initial_calls

    def test_empty_items_nepisodes(self):
        p = _mock_podcast(RSS_EMPTY_ITEMS)
        assert p.nepisodes == 0


class TestCounterFormatting:

    def test_episode_counters(self):
        p = _mock_podcast(SAMPLE_RSS_XML, folder="/tmp",
                          filename_template="$inumber of $nepisodes - $title")
        epi0 = p.episode(0)
        epi1 = p.episode(1)
        assert epi0 is not None
        assert epi1 is not None
        fname0 = epi0._Episode__local_filename
        fname1 = epi1._Episode__local_filename
        assert "1 of 2" in fname0
        assert "2 of 2" in fname1
