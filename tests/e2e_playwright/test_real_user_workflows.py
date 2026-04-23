from playwright.sync_api import Page, expect


def test_login_and_dashboard_render(page: Page, login):
    login()


def test_intake_workflow_ui_elements(page: Page, login):
    login()
    page.locator("a:has-text('Intake')").first.click()
    expect(page.get_by_text('Intake Mode').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Initial Intake (New Case)').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Supplemental Intake').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Collection Method').first).to_be_visible(timeout=30000)
    expect(page.get_by_text('Harvested').first).to_be_visible(timeout=30000)
    page.get_by_role('button', name='SAVE').click()
    expect(page.get_by_text('Finder or Turtle Name is required').first).to_be_visible(timeout=30000)
