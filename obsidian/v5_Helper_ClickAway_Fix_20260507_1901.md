---
date: 2026-05-07T19:01:41.103585
tags: [qa, fix, v5-helper, click-away]
status: applied
---

# v5 Helper Click-Away Fix + TSK-07 Guard

## Changes Made
- **streamlit_select_helper.py**: Added click-away after popover option selection (clicks body to dismiss popover, triggering Streamlit's on_change handler)
- **streamlit_select_helper.py**: Added post-selection verification via DOM check
- **test_phase5_scalability_loop.py**: Added retry guard around workbench_bins population

## Rationale
Claude batch v3 revealed Stage selectbox clicks work (option found and clicked) but selection doesn't persist. Root cause: clicking the popover LI doesn't close the popover, so Streamlit's on_change never fires. Click-away forces popover dismissal.

## Previous Red Team Recommendations Status
1. ✅ Pass params via Playwright args — already implemented
2. ✅ scroll_into_view before bounding_box — already in open_selectbox_popover()
3. ✅ Post-selection verification — added now via DOM check
4. ✅ Remove double-click bug — verified no double-click in helper code
5. ✅ Use page.evaluate() exclusively for popovers — already implemented
