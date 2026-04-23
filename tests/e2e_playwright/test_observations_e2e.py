from playwright.sync_api import Page, expect


def test_observation_grid_and_correction_mode(page: Page, login):
    login()
    page.locator("a:has-text('Observations')").first.click()
    expect(page.get_by_role('heading', name='Observations')).to_be_visible(timeout=30000)
    expect(page.get_by_text('Correction Mode').first).to_be_visible(timeout=30000)
    expect(page.get_by_role('button', name='SAVE').first).to_be_visible(timeout=30000)
