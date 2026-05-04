from playwright.sync_api import Page, expect
from e2e_selectors import NAV_OBSERVATIONS, HEADING_OBSERVATIONS


def test_observation_grid_and_correction_mode(page: Page, login):
    login()
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role('heading', name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)
    expect(page.get_by_text('Correction Mode').first).to_be_visible(timeout=30000)
    expect(page.get_by_role('button', name='SAVE').first).to_be_visible(timeout=30000)
