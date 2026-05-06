import pytest
import db_verify_TC_LOGIN_001



@pytest.mark.e2e
def test_login_splash_to_dashboard(login, verify_version, page, e2e_base_url):
    # Already on dashboard after successful login (login fixture handles START click)
    login()
    # 1. Verify dashboard heading
    heading = page.get_by_role("heading", name="Today's Summary", exact=True)
    assert heading.is_visible(), "Dashboard heading 'Today's Summary' must be visible after login"

    # 2. Verify sidebar contains version string
    sidebar = page.locator('[data-testid="stSidebar"]')
    version_text = sidebar.get_by_text("v9.2.0")
    assert version_text.first.is_visible(), "Sidebar must display version v9.2.0"

    # 3. Verify version via settings page fixture
    verify_version("v9.2.0")
    # 4. DB verification (Blind Pincer - DB Auditor module)
    db_verify_TC_LOGIN_001.verify_login_db_state()
