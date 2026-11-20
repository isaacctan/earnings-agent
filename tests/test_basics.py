"""Small automatic checks. Run them all by typing:   pytest"""

from agent.parse import html_to_text
from agent.sec_client import pick_press_release


def test_picks_exhibit_99_1():
    files = [("rm-20261104.htm", 40000), ("rm-ex99_1.htm", 300000), ("rm-ex99_2.htm", 900000)]
    assert pick_press_release(files, "rm-20261104.htm") == "rm-ex99_1.htm"


def test_picks_exhibit_with_no_separator():
    files = [("form8k.htm", 40000), ("ex992.htm", 500000), ("ex991.htm", 300000)]
    assert pick_press_release(files, "form8k.htm") == "ex991.htm"


def test_falls_back_to_biggest_page():
    files = [("form8k.htm", 40000), ("pressrelease.htm", 300000), ("logo.jpg", 999999)]
    assert pick_press_release(files, "form8k.htm") == "pressrelease.htm"


def test_table_rows_stay_on_one_line():
    html = "<p>Results</p><table><tr><td>Revenue</td><td>$</td><td>165.5</td></tr></table>"
    assert "Revenue | $ | 165.5" in html_to_text(html)
