"""
Branding Compliance — §1 UI Vocabulary Standard.
Verifies that bootstrap.py CSS block contains the required SAVE/CANCEL color tokens
and that the Hatching Turtle loading indicator is present.
"""
import pathlib


def test_save_button_color_token_in_bootstrap():
    """SAVE buttons must be styled green (#10b981) per §1 branding standard."""
    css = pathlib.Path("utils/bootstrap.py").read_text(encoding="utf-8")
    assert "#10b981" in css, "SAVE button green color token (#10b981) missing from bootstrap CSS."
    assert "SAVE" in css, "SAVE button selector missing from bootstrap CSS."


def test_cancel_button_color_token_in_bootstrap():
    """CANCEL buttons must be styled red (#ef4444) per §1 branding standard."""
    css = pathlib.Path("utils/bootstrap.py").read_text(encoding="utf-8")
    assert "#ef4444" in css, "CANCEL button red color token (#ef4444) missing from bootstrap CSS."


def test_hatching_turtle_loading_indicator_present():
    """🐢 loading indicator must be present — replacing the default Streamlit spinner."""
    css = pathlib.Path("utils/bootstrap.py").read_text(encoding="utf-8")
    assert "stStatusWidget" in css, "Hatching Turtle stStatusWidget override missing from bootstrap CSS."
    assert "🐢" in css, "Hatching Turtle emoji missing from bootstrap CSS."
