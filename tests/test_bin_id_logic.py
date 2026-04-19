import pytest
import re

def generate_bin_id(species_code, intake_count, finder_name, bin_num):
    """
    Replicates the logic from vault_views/2_New_Intake.py
    """
    finder_clean = str(re.sub(r"[^A-Z0-9]", "", finder_name.upper()))
    return f"{species_code}-{intake_count}-{finder_clean}-{bin_num}"

def test_standard_bin_id_format():
    # SpeciesCode-IntakeCount-Name-BinNumber
    species_code = "CH"
    intake_count = 12
    finder_name = "John Doe"
    bin_num = 1
    
    expected = "CH-12-JOHNDOE-1"
    assert generate_bin_id(species_code, intake_count, finder_name, bin_num) == expected

def test_bin_id_with_special_characters():
    # Cleaning check
    species_code = "MK"
    intake_count = 5
    finder_name = "O'Malley-Smith"
    bin_num = 2
    
    expected = "MK-5-OMALLEYSMITH-2"
    assert generate_bin_id(species_code, intake_count, finder_name, bin_num) == expected

def test_bin_id_with_numbers_in_name():
    species_code = "SN"
    intake_count = 1
    finder_name = "Unit 404"
    bin_num = 3
    
    expected = "SN-1-UNIT404-3"
    assert generate_bin_id(species_code, intake_count, finder_name, bin_num) == expected

if __name__ == "__main__":
    pytest.main([__file__])
