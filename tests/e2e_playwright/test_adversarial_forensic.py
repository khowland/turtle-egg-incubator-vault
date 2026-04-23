import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase

def login(page: Page):
    page.goto("http://localhost:8501")
    if page.locator("text=START SHIFT").is_visible():
        page.locator("text=Kevin Howland").click()
        page.locator("text=START SHIFT").click()
    expect(page.locator("text=Today's Summary")).to_be_visible(timeout=10000)

def test_layer1_adversarial_ui_rejections(page: Page):
    login(page)
    page.locator("a:has-text('Intake')").first.click()
    expect(page.locator("text=📁 Step 1: Mother Turtle Info")).to_be_visible(timeout=10000)

    # Attempt to save an empty form to trigger validations
    page.locator("text=SAVE").click()
    expect(page.locator("text=Finder or Turtle Name is required")).to_be_visible(timeout=10000)

def test_layer2_forensic_backend_verification(page: Page):
    login(page)
    page.locator("a:has-text('Intake')").first.click()
    expect(page.locator("text=📁 Step 1: Mother Turtle Info")).to_be_visible(timeout=10000)
    
    unique_sig = f"FORENSIC-{int(time.time())}"
    
    page.fill("input[aria-label='Finder']", unique_sig)
    page.fill("input[aria-label='WINC Case #']", unique_sig)
    
    page.locator("text=Natural").first.click()
    page.locator("text=Harvested").first.click()
    
    page.locator("text=SAVE").click()
    expect(page.locator("text=Observations & Daily Checks")).to_be_visible(timeout=15000)
    
    # Forensic Database Assertions
    db = get_supabase()
    intake_res = db.table('intake').select('*').eq('intake_name', unique_sig).execute()
    assert len(intake_res.data) == 1, "DB FAILURE: Intake row missing!"
    intake_record = intake_res.data[0]
    
    metadata = intake_record.get('clinical_metadata', {})
    assert metadata.get('collection_method') == 'Harvested', "DB FAILURE: JSONB metadata failed to save!"
    
    bin_res = db.table('bin').select('*').eq('intake_id', intake_record['intake_id']).execute()
    assert len(bin_res.data) == 1, "DB FAILURE: Bin row missing!"
    bin_id = bin_res.data[0]['bin_id']
    
    egg_res = db.table('egg').select('*').eq('bin_id', bin_id).execute()
    assert len(egg_res.data) == 1, "DB FAILURE: Egg row missing or count mismatch!"
    egg_id = egg_res.data[0]['egg_id']
    assert egg_res.data[0]['current_stage'] == 'S1', "DB FAILURE: Egg did not default to Stage 1!"
    
    obs_res = db.table('egg_observation').select('*').eq('egg_id', egg_id).execute()
    assert len(obs_res.data) == 1, "DB FAILURE: S1 Baseline Observation was NOT generated!"
    assert obs_res.data[0]['stage_at_observation'] == 'S1', "DB FAILURE: Baseline stage incorrect!"
