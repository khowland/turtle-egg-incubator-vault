from playwright.sync_api import Page, expect


def test_initial_intake_validation_and_ui(page: Page, login):
    login()
    page.locator("a:has-text('Intake')").first.click()
    expect(page.get_by_role('heading', name='Step 1: Mother Turtle Info')).to_be_visible(timeout=30000)
    page.get_by_role('button', name='SAVE').click()
    expect(page.get_by_text('Finder or Turtle Name is required').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('WINC Case #').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Collection Method').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Harvested').first).to_be_visible(timeout=30000)


def test_supplemental_intake_workflow(page: Page, login):
    login()
    page.locator("a:has-text('Intake')").first.click()
    expect(page.get_by_role('heading', name='Step 1: Mother Turtle Info')).to_be_visible(timeout=30000)
    page.locator("label:has-text('Supplemental Intake')").first.click()
    expect(page.get_by_text('Supplemental Mode Active').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Select Existing Mother').first).to_be_visible(timeout=30000)
