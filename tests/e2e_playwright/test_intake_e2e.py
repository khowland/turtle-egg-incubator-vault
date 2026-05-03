from e2e_selectors import NAV_INTAKE
from playwright.sync_api import Page, expect

def test_initial_intake_validation_and_ui(page: Page, login):
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role('heading', name='Step 1: Mother Turtle Info')).to_be_visible(timeout=30000)
    page.get_by_role('button', name='SAVE').click()
    expect(page.get_by_text('Finder or Turtle Name is required').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('WINC Case #').first).to_be_visible(timeout=30000)
    # CR-20260430-194500: Updated selector for renamed label
    expect(page.get_by_text('Egg Collection Method').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Harvested').first).to_be_visible(timeout=30000)

def test_supplemental_intake_workflow(page: Page, login):
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role('heading', name='Step 1: Mother Turtle Info')).to_be_visible(timeout=30000)
    # CR-20260430-194500: Updated selector for renamed label
    page.locator("label:has-text('Add Eggs or Bins to Existing Intake')").first.click()
    expect(page.get_by_text('Supplemental Mode Active').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Select Existing Mother').first).to_be_visible(timeout=30000)
