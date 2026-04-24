import pytest
from unittest.mock import MagicMock


SAMPLE_RSS_XML = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <description>A test podcast feed</description>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test Image</title>
        <link>https://example.com/</link>
    </image>
    <item>
        <title>Episode One</title>
        <link>https://example.com/episode-one</link>
        <description>Description of episode one</description>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
        <enclosure url="https://example.com/ep1.mp3"
            type="audio/mpeg" length="1000"/>
    </item>
    <item>
        <title>Episode Two</title>
        <link>https://example.com/episode-two</link>
        <description>Description of episode two</description>
        <pubDate>Fri, 28 Jan 2022 10:00:00 +0100</pubDate>
        <enclosure url="https://example.com/ep2.ogg"
           type="audio/ogg" length="2000"/>
    </item>
</channel>
</rss>"""

RSS_NO_DESCRIPTION = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test</title>
        <link>https://example.com/</link>
    </image>
    <item>
        <title>Episode One</title>
        <link>https://example.com/episode-one</link>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
        <enclosure url="https://example.com/ep1.mp3"
           type="audio/mpeg" length="1000"/>
    </item>
</channel>
</rss>"""

RSS_NO_LINK = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <description>A test feed</description>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test</title>
        <link>https://example.com/</link>
    </image>
    <item>
        <title>Episode One</title>
        <link>https://example.com/episode-one</link>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
        <enclosure url="https://example.com/ep1.mp3"
            type="audio/mpeg" length="1000"/>
    </item>
</channel>
</rss>"""

RSS_NO_IMAGE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <description>A test feed</description>
    <item>
        <title>Episode One</title>
        <link>https://example.com/episode-one</link>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
        <enclosure url="https://example.com/ep1.mp3"
            type="audio/mpeg" length="1000"/>
    </item>
</channel>
</rss>"""

RSS_NO_ENCLOSURE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <description>A test feed</description>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test</title>
        <link>https://example.com/</link>
    </image>
    <item>
        <title>Episode Without Audio</title>
        <link>https://example.com/episode</link>
        <description>No audio file</description>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
    </item>
</channel>
</rss>"""

RSS_ITEM_NO_LINK = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <description>A test feed</description>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test</title>
        <link>https://example.com/</link>
    </image>
    <item>
        <title>Episode Without Link</title>
        <description>No link element</description>
        <pubDate>Mon, 31 Jan 2022 18:43:00 +0100</pubDate>
        <enclosure url="https://example.com/ep.mp3"
            type="audio/mpeg" length="1000"/>
    </item>
</channel>
</rss>"""

RSS_EMPTY_ITEMS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>Test Podcast</title>
    <link>https://example.com/</link>
    <description>A test feed</description>
    <image>
        <url>https://example.com/image.png</url>
        <title>Test</title>
        <link>https://example.com/</link>
    </image>
</channel>
</rss>"""


def _make_mock_response(content, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.content = (
        content.encode("utf-8") if isinstance(content, str)
        else content
    )
    mock_resp.headers = {"Content-Length": "1024"}
    mock_resp.iter_content = (
        lambda chunk_size=1024: iter(
            [content.encode("utf-8")[:chunk_size]]
        )
    )
    return mock_resp


@pytest.fixture(autouse=True)
def reset_verbose():
    import pypodget.globals as g
    original = g.__verbose__
    g.__verbose__ = True
    yield
    g.__verbose__ = original


@pytest.fixture
def sample_rss_xml():
    return SAMPLE_RSS_XML


@pytest.fixture
def mock_requests_get(sample_rss_xml):
    with pytest.importorskip("unittest.mock").patch(
        "pypodget.podcast.requests.get"
    ) as mock_get:
        mock_get.return_value = _make_mock_response(sample_rss_xml)
        yield mock_get


@pytest.fixture
def tmp_folder(tmp_path):
    return str(tmp_path)


@pytest.fixture
def sample_config_file(tmp_path):
    config_text = """[TestPodcast]
url = https://example.com/feed.xml
directory = ./test_output/
filename = $year-$month-$day - $title.$ext
"""
    p = tmp_path / "test_config.ini"
    p.write_text(config_text)
    return str(p)


@pytest.fixture
def config_missing_url(tmp_path):
    config_text = """[TestPodcast]
directory = ./test_output/
"""
    p = tmp_path / "bad_config.ini"
    p.write_text(config_text)
    return str(p)


@pytest.fixture
def config_missing_directory(tmp_path):
    config_text = """[TestPodcast]
url = https://example.com/feed.xml
"""
    p = tmp_path / "bad_config2.ini"
    p.write_text(config_text)
    return str(p)
