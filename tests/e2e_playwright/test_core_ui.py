from e2e_selectors import HEADING_DASHBOARD
from playwright.sync_api import Page, expect

def test_dashboard_renders(page: Page, login):
    login()
    title = page.get_by_role('heading', name=HEADING_DASHBOARD).first
    expect(title).to_be_visible(timeout=30000)
    font_family = title.evaluate("el => getComputedStyle(el).fontFamily")
    assert 'Source Sans' in font_family
