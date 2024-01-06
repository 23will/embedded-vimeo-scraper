import unittest
from src.html_parser import HtmlParser


class HtmlParserTestCase(unittest.TestCase):
    def test_parse_href(self):
        html = """<a class="c1" href="https://something.com/blah/"></a>"""
        parser = HtmlParser([], html, "https://something.com")
        hrefs = parser.find_urls()
        self.assertIs(len(hrefs), 1)


if __name__ == "__main__":
    unittest.main()
