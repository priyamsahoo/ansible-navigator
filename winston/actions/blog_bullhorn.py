""" :blog """
import logging
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import webbrowser

from typing import List
from typing import NamedTuple
from typing import Union
from xml.etree.ElementTree import Element

from . import _actions as actions
from ..app import App
from ..ui import Interaction


class Blog(NamedTuple):
    """simplent for a blog post"""

    title: Union[str, None]
    link: Union[str, None]
    date: Union[str, None]
    category: Union[str, None]


URLS = {
    "blog": "https://www.ansible.com/blog/rss.xml",
    "bullhorn": "https://us19.campaign-archive.com/feed?u=56d874e027110e35dea0e03c1&id=d6635f5420",
    "redhat": "https://www.redhat.com/sysadmin/rss.xml",
}


@actions.register
class Action:
    """:blog"""

    # pylint: disable=too-few-public-methods

    KEGEX = r"^(?P<rss>blog|bullhorn|redhat)$"

    def __init__(self):
        self._logger = logging.getLogger()

    def run(self, interaction: Interaction, app: App) -> bool:
        """Handle <esc>

        :param interaction: The interaction from the user
        :type interaction: Interaction
        :param app: The app instance
        :type app: App
        """
        self._logger.debug("blog requested")

        url = URLS.get(str(interaction.action.value), None)
        if not url:
            self._logger.debug("no url for %s", interaction.action.value)
            return True

        previous_filter = interaction.ui.menu_filter()
        interaction.ui.menu_filter(None)

        previous_scroll = interaction.ui.scroll()
        interaction.ui.scroll(0)

        interaction.ui.show(obj="Collecting contents...", xform="text", await_input=False)
        interaction.ui.scroll(0)

        root = self._get_and_parse_feed(url)
        if root is not None:
            feed = self._parse_feed(root)
            if feed:
                columns = ["title", "date"]
                if any(blog.category for blog in feed):
                    columns = ["category", "title", "date"]
                else:
                    columns = ["title", "date"]
                f2show = [blog._asdict() for blog in feed]
            else:
                self._logger.info("feed empty")
                return True
        else:
            self._logger.info("blog was empty")
            return True

        while True:
            result = interaction.ui.show(obj=f2show, columns=columns)
            app.update()
            if result.action.name == "select":
                webbrowser.open_new_tab(f2show[result.action.value % len(f2show)]["link"])
            elif result.action.name != "refresh":
                break

        interaction.ui.scroll(previous_scroll)
        interaction.ui.menu_filter(previous_filter)

        return result

    @staticmethod
    def _get_text(ement: Element, name: str) -> Union[str, None]:
        ele = ement.find(name)
        if ele is not None:
            return ele.text
        return ele

    def _parse_feed(self, root: Element) -> List[Blog]:
        channel = root.find("channel")
        if channel is not None:
            feed = [
                Blog(
                    title=self._get_text(element, "title"),
                    link=self._get_text(element, "link"),
                    date=self._get_text(element, "pubDate"),
                    category=self._get_text(element, "category"),
                )
                for element in channel.iterfind("item")
            ]
            return feed
        return []

    def _get_and_parse_feed(self, url: str) -> Union[Element, None]:
        html = self._get_feed(url)
        if not html:
            return None
        return self._parse_html(html)

    def _get_feed(self, url: str) -> Union[str, None]:
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                return html.decode()
        except urllib.error.URLError:
            self._logger.info("blog url get failed")
            return None

    def _parse_html(self, html: str) -> Union[Element, None]:
        try:
            root = ET.fromstring(html)
            return root
        except ET.ParseError:
            self._logger.info("xml parse of blog failed")
            return None
