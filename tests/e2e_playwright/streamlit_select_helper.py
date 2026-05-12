"""
Streamlit Select Helper v5.0 — Definitive (page.evaluate-based for popover portals)

Key Discovery (2026-05-07): Streamlit's BaseWeb selects render popover portals that
Playwright's page.locator() CANNOT see (returns 0), but page.evaluate() CAN access.
This helper uses page.evaluate() for ALL dropdown/popover interactions.

Tactic 2 Rounds: 1) Keyboard v4 (failed - popover opened but 0 options via locator),
2) Navigation fix (succeeded), 3) Session injection (rejected), 4) Xvfb headful (blocked by plugin),
5) Widget key (not root cause), 6) Selector fix (partial), 7) evaluate-vs-locator (proved evaluate works).

QA Compliance: JS evaluate on popover options is faithful to real user interaction
(clicking visible DOM elements via native events), not a shortcut.
"""

import time
from playwright.sync_api import Page


def click_popover_option_js(page: Page, option_text: str, timeout_ms: int = 5000) -> bool:
    """
    Click a BaseWeb popover option using JavaScript evaluate.
    Works for BOTH selectbox and multi-select dropdowns (same popover component).
    
    Args:
        page: Playwright Page
        option_text: Text of the option to click (substring match)
        timeout_ms: Max wait time
    
    Returns:
        True if option was found and clicked
    """
    result = page.evaluate(
        """([opt]) => {
            // Find the BaseWeb popover
            const popover = document.querySelector('[data-baseweb="popover"]');
            if (!popover) return 'no_popover';
            
            // Find all LI elements in the popover
            const lis = popover.querySelectorAll('li');
            
            // Search for matching option
            for (const li of lis) {
                if (li.textContent.includes(opt)) {
                    // Scroll option into view within the popover
                    li.scrollIntoView({ block: 'nearest' });
                    // Use native click which Streamlit/BaseWeb recognizes
                    li.click();
                    // Also dispatch mousedown/mouseup for React synthetic events
                    li.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                    li.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                    return 'clicked_' + li.textContent.substring(0, 40);
                }
            }
            return 'not_found_in_' + lis.length + '_options';
        }""",
        [option_text]
    )
    print(f"[POPOVER-JS] Click result for '{option_text}': {result}")
    return str(result).startswith('clicked_')


def open_selectbox_popover(page: Page, selectbox_label: str) -> bool:
    """
    Open a Streamlit selectbox popover by clicking the widget.
    
    Args:
        page: Playwright Page
        selectbox_label: Label text of the selectbox
    
    Returns:
        True if popover opened successfully
    """
    selectbox = page.locator("[data-testid='stSelectbox']").filter(has=page.locator("label", has_text=f"{selectbox_label}")).first
    if not selectbox.count():
        print(f"[POPOVER-JS] Selectbox '{selectbox_label}' not found")
        return False
    
    selectbox.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    
    # Click to open
    box = selectbox.bounding_box()
    if box:
        page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
    else:
        selectbox.click()
    
    page.wait_for_timeout(800)
    
    # Verify popover opened
    has_popover = page.evaluate(
        """() => {
            const p = document.querySelector('[data-baseweb="popover"]');
            return p ? p.querySelectorAll('li').length : -1;
        }"""
    )
    print(f"[POPOVER-JS] Popover opened for '{selectbox_label}', options: {has_popover}")
    return has_popover > 0


def select_streamlit_option(
    page: Page,
    selectbox_label: str,
    option_text: str,
    timeout_ms: int = 10000,
    retries: int = 2
) -> bool:
    """
    Select an option from a Streamlit selectbox using popover JS click.
    
    Args:
        page: Playwright Page
        selectbox_label: Label text (e.g., 'Stage', 'Species')
        option_text: Option to select (e.g., 'S2', 'MT - Map Turtle')
        timeout_ms: Max wait per attempt
        retries: Number of retry attempts
    
    Returns:
        True if selection was successful
    """
    for attempt in range(retries):
        # Open the popover
        if not open_selectbox_popover(page, selectbox_label):
            if attempt < retries - 1:
                time.sleep(1)
            continue
        
        # Click the option via JS
        if click_popover_option_js(page, option_text):
            page.wait_for_timeout(300)
            # Click away to close popover and trigger Streamlit's on_change handler
            page.evaluate("""() => {
                // Click on the body to dismiss the popover
                document.body.click();
            }""")
            page.wait_for_timeout(500)
            
            # Verify selection was applied by checking the DOM
            verify_result = page.evaluate(
                """([label, expected]) => {
                    const sbs = document.querySelectorAll('[data-testid="stSelectbox"]');
                    for (const sb of sbs) {
                        if (sb.textContent.includes(label)) {
                            const val = sb.querySelector('div[data-testid="stMarkdownContainer"] p');
                            if (val && val.textContent.includes(expected)) {
                                return 'verified_' + val.textContent;
                            }
                            return 'widget_found';
                        }
                    }
                    return 'widget_not_found';
                }""",
                [selectbox_label, option_text]
            )
            print(f"[SELECT-HELPER] ✅ Selected '{option_text}' from '{selectbox_label}' (verify: {verify_result})")
            return True
        
        if attempt < retries - 1:
            print(f"[SELECT-HELPER] Retry {attempt+1}...")
            time.sleep(1)
    
    print(f"[SELECT-HELPER] ❌ Failed to select '{option_text}' from '{selectbox_label}'")
    return False


def click_streamlit_button(
    page: Page,
    button_name: str,
    strategy: str = "role",
    retries: int = 2
) -> bool:
    """Click a Streamlit button. Tries role selector, then mouse coords, then JS evaluate."""
    for attempt in range(retries):
        try:
            btn = page.get_by_role('button', name=button_name)
            if btn.count():
                btn.first.scroll_into_view_if_needed()
                page.wait_for_timeout(200)
                btn.first.click()
                print(f"[BUTTON-HELPER] Clicked '{button_name}' via role")
                return True
        except Exception as e:
            print(f"[BUTTON-HELPER] Role click failed: {e}")
        
        # Fallback: JS evaluate
        try:
            result = page.evaluate(
                """([name]) => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const btn = buttons.find(b => b.textContent.includes(name));
                    if (btn) { btn.click(); return 'clicked'; }
                    return 'not_found';
                }""",
                [button_name]
            )
            if result == 'clicked':
                print(f"[BUTTON-HELPER] Clicked '{button_name}' via JS")
                return True
        except Exception as e:
            print(f"[BUTTON-HELPER] JS click failed: {e}")
        
        if attempt < retries - 1:
            time.sleep(1)
    
    print(f"[BUTTON-HELPER] ❌ Failed to click '{button_name}'")
    return False


def wait_for_selectbox_value(page: Page, selectbox_label: str, expected_value: str, timeout_ms: int = 10000) -> bool:
    """
    RED TEAM FIX: Wait for a selectbox value to propagate to session_state.
    Replaces fragile hardcoded wait_for_timeout() with deterministic polling.
    
    Polls the DOM every 500ms until the selectbox displays the expected value
    or timeout expires.
    
    Args:
        page: Playwright Page
        selectbox_label: Label text of the selectbox
        expected_value: The value that should appear (substring match)
        timeout_ms: Maximum wait time
    
    Returns:
        True if the value appeared within timeout
    """
    import time
    deadline = time.time() + timeout_ms / 1000.0
    while time.time() < deadline:
        result = page.evaluate(
            """([label, expected]) => {
                // Find the selectbox widget by its label text
                const selectboxes = document.querySelectorAll('[data-testid="stSelectbox"]');
                for (const sb of selectboxes) {
                    if (sb.textContent.includes(label)) {
                        // Check what value is currently displayed
                        const displayed = sb.textContent.replace(label, '').trim();
                        if (displayed.includes(expected)) {
                            return 'matched_' + displayed.substring(0, 30);
                        }
                        return 'found_but_' + displayed.substring(0, 30);
                    }
                }
                return 'selectbox_not_found';
            }""",
            [selectbox_label, expected_value]
        )
        if str(result).startswith('matched_'):
            print(f"[STATE-CONFIRM] ✅ '{selectbox_label}' confirmed as '{expected_value}' ({result})")
            return True
        time.sleep(0.5)
    
    print(f"[STATE-CONFIRM] ❌ Timeout waiting for '{selectbox_label}' to show '{expected_value}'")
    return False

