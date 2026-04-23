import os
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope='session')
def e2e_base_url() -> str:
    return os.environ.get('E2E_BASE_URL', 'http://127.0.0.1:8501')


@pytest.fixture()
def login(page: Page, e2e_base_url: str):
    def _login():
        page.goto(e2e_base_url, wait_until='domcontentloaded')
        expect(page.get_by_role('button', name='START', exact=True)).to_be_visible(timeout=30000)
        page.get_by_role('button', name='START', exact=True).click()
        expect(page.get_by_role('heading', name="Today's Summary")).to_be_visible(timeout=30000)
    return _login
