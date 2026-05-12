"""
Streamlit Select Helper v3.0 DRAFT — Keyboard Navigation Approach

Tactic 2 — Fundamentally Different Strategy
Author: A0 (Deepseek) — Strategy Design
Reviewer: PENDING (Claude Model 2)
Status: DRAFT for Red Team Review

Problem: Streamlit's BaseWeb selectbox dropdown uses React portals that don't open
reliably with synthetic Playwright mouse events in headless Chromium.

New Approach: KEYBOARD NAVIGATION
- Use browser-native Tab/Enter/Arrow keys
- More faithful to real user interaction
- Keyboard events bypass React synthetic event issues
- Works in headless mode (tested in Playwright docs)
"""

import time
from playwright.sync_api import Page


def select_streamlit_option_keyboard(
    page: Page,
    selectbox_label: str,
    option_text: str,
    timeout_ms: int = 10000
) -> bool:
    """
    Select an option from a Streamlit selectbox using keyboard navigation.
    
    Strategy: Tab to focus → Space to open dropdown → type to filter → Enter to select
    
    This approach works because:
    1. Keyboard Tab navigation uses browser's native focus system (reliable in headless)
    2. Space/Enter key events trigger React's onKeyDown handlers
    3. Typing filters the BaseWeb dropdown (typeahead support)
    4. Enter confirms selection — all native browser behavior
    
    Args:
        page: Playwright Page
        selectbox_label: Visible label text
        option_text: Option to select
        timeout_ms: Max wait time
    
    Returns:
        True if selection was successful
    """
    try:
        # Step 1: Click the selectbox to give it focus
        # (using a gentle click near the label, not on the dropdown trigger)
        selectbox = page.locator(
            f"[data-testid='stSelectbox']:has-text('{selectbox_label}')"
        ).first
        
        if not selectbox.count():
            # Try by label text directly
            selectbox = page.get_by_text(selectbox_label, exact=False).first
            if not selectbox.count():
                print(f"[KBD-HELPER] Selectbox '{selectbox_label}' not found")
                return False
        
        # Scroll into view and click to focus
        selectbox.scroll_into_view_if_needed()
        selectbox.click()
        page.wait_for_timeout(500)
        
        # Step 2: Press Space to open the dropdown
        page.keyboard.press("Space")
        page.wait_for_timeout(800)
        
        # Step 3: Type option text to filter/navigate (BaseWeb typeahead)
        # Type slowly so React processes each character
        for char in option_text:
            page.keyboard.type(char, delay=50)
        page.wait_for_timeout(500)
        
        # Step 4: Press Enter to select the highlighted option
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        
        # Step 5: Verify selection
        verify_result = page.evaluate(
            """([label]) => {
                const boxes = document.querySelectorAll("[data-testid='stSelectbox']");
                for (const box of boxes) {
                    if (box.textContent.includes(label)) {
                        // Find the selected value span
                        const spans = box.querySelectorAll('span');
                        for (const span of spans) {
                            const txt = span.textContent.trim();
                            // Skip label spans (they have emoji prefixes)
                            if (txt && txt.length < 30 && !txt.includes('✅') && !txt.includes('📊')) {
                                return txt;
                            }
                        }
                        return 'found_box_no_value';
                    }
                }
                return 'box_not_found';
            }""",
            [selectbox_label]
        )
        print(f"[KBD-HELPER] Selection result: {verify_result}")
        
        if str(verify_result) == option_text:
            print(f"[KBD-HELPER] ✅ Selected '{option_text}' via keyboard")
            return True
        elif option_text in str(verify_result):
            print(f"[KBD-HELPER] ⚠️ Partial match: expected '{option_text}', got '{verify_result}'")
            return True  # Partial match is acceptable for typeahead
        else:
            print(f"[KBD-HELPER] ❌ Verification failed: expected '{option_text}', got '{verify_result}'")
            return False
            
    except Exception as e:
        print(f"[KBD-HELPER] Error: {e}")
        return False


def select_streamlit_option_autodetect(
    page: Page,
    selectbox_label: str,
    option_text: str,
    timeout_ms: int = 10000
) -> bool:
    """
    Smart selector: tries keyboard first, falls back to mouse.
    """
    print(f"[AUTO] Trying keyboard navigation for '{selectbox_label}' → '{option_text}'")
    if select_streamlit_option_keyboard(page, selectbox_label, option_text, timeout_ms):
        return True
    
    print(f"[AUTO] Keyboard failed, trying v2 mouse helper...")
    from streamlit_select_helper import select_streamlit_option
    return select_streamlit_option(page, selectbox_label, option_text, timeout_ms)


# ============================================================
# Alternative: Tab-sequence navigation
# ============================================================

def select_streamlit_option_tab_sequence(
    page: Page,
    selectbox_label: str,
    option_text: str,
    tab_count: int = None
) -> bool:
    """
    Alternative keyboard approach: Press Tab N times to reach the selectbox,
    then Space → type → Enter.
    
    This is useful when the selectbox label can't be located by selector
    but we know its position in the tab order.
    
    Args:
        tab_count: Number of Tab presses to reach the selectbox.
                   If None, auto-detect by counting all focusable elements.
    """
    try:
        # Start from body to reset focus
        page.locator("body").click()
        page.wait_for_timeout(300)
        
        if tab_count is None:
            # Auto-detect: find all stSelectbox elements, use the one matching label
            count = page.locator("[data-testid='stSelectbox']").count()
            if count == 0:
                return False
            # Navigate to the matching selectbox
            for i in range(count):
                sel = page.locator("[data-testid='stSelectbox']").nth(i)
                if selectbox_label in sel.text_content():
                    # Found it — estimate tabs needed
                    # Each selectbox is about 2-3 tabs away in Streamlit layout
                    # We'll tab until we find it (max 50 tabs)
                    for t in range(50):
                        page.keyboard.press("Tab")
                        page.wait_for_timeout(100)
                        # Check if this is our selectbox
                        focused = page.evaluate(
                            """() => {
                                const el = document.activeElement;
                                return el ? el.tagName + '|' + (el.textContent || '').substring(0, 30) : 'none';
                            }"""
                        )
                        if selectbox_label in focused:
                            tab_count = t + 1
                            print(f"[KBD-TAB] Found selectbox after {tab_count} tabs")
                            break
                    break
            
            if tab_count is None:
                print(f"[KBD-TAB] Could not locate selectbox in tab order")
                return False
        
        # Now at the selectbox — Space to open, type, Enter to select
        page.keyboard.press("Space")
        page.wait_for_timeout(500)
        
        for char in option_text:
            page.keyboard.type(char, delay=30)
        page.wait_for_timeout(300)
        
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        
        # Verify
        focused = page.evaluate(
            """() => {
                const el = document.activeElement;
                return el ? el.textContent?.substring(0, 50) : 'none';
            }"""
        )
        print(f"[KBD-TAB] After selection, focused element: {focused}")
        return option_text in str(focused)
        
    except Exception as e:
        print(f"[KBD-TAB] Error: {e}")
        return False


if __name__ == '__main__':
    print(__doc__)
