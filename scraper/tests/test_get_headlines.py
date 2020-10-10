from get_headlines import *


def test_clean_text():
    assert clean_text("\n A Headline \n ") == "a headline"


def test_display_text():
    assert display_text("\n A Headline \n ") == "A Headline"


def test_get_base_url():
    assert get_base_url("http://www.bbc.co.uk/news") == "http://www.bbc.co.uk/"


