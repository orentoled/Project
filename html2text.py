import re

import mistletoe
from bs4 import BeautifulSoup
from mistletoe import markdown
from html2text import HTML2Text




# md = HTML2Text().handle(html)
# html2 = markdown(md)
# text = BeautifulSoup(html2).getText()
#
#
# html_simple = mistletoe.markdown(md)
# text = BeautifulSoup(html_simple).getText()


def normalise_markdown_lists(md):
    return re.sub(r"(^|\n) ? ? ?\\?[.--*]( \w)", r'\1  *\2', md)


def html2plain(html):
    md = html2md(html)
    md = normalise_markdown_lists(md)
    html_simple = mistletoe.markdown(md)
    text = BeautifulSoup(html_simple).getText()
    text = fixup_markdown_formatting(text)
    return text


def html2md(html):
    parser = HTML2Text()
    parser.ignore_images = True
    parser.ignore_anchors = True
    parser.body_width = 0
    md = parser.handle(html)
    return md


def fixup_markdown_formatting(text):
    # Strip off table formatting
    text = re.sub(r'(^|\n)\|\s*', r'\1', text)
    # Strip off extra emphasis
    text = re.sub(r'\*\*', '', text)
    # Remove trailing whitespace and leading newlines
    text = re.sub(r' *$', '', text)
    text = re.sub(r'\n\n+', r'\n\n', text)
    text = re.sub(r'^\n+', '', text)
    return text