import pytest
import re

def generate_bin_code(species_code, intake_count, finder_name, bin_num):  # CR-20260501-1800: Renamed from generate_bin_id; now generates text bin_code
    """
    Replicates the bin_code generation logic from vault_views/2_New_Intake.py
    """
    finder_clean = str(re.sub(r"[^A-Z0-9'\-.]", "", finder_name.upper()))  # CR-20260501-1800: Allow apostrophes, hyphens, periods
    return f"{species_code}{intake_count}-{finder_clean}-{bin_num}"  # CR-20260501-1800: SpeciesCode+IntakeNum-Finder-BinNum format

def test_standard_bin_code_format():  # CR-20260501-1800: Renamed test
    # SpeciesCode{IntakeNum}-Finder-BinNum
    species_code = "CH"
    intake_count = 12
    finder_name = "John Doe"
    bin_num = 1
    
    expected = "CH13-JOHNDOE-1"  # CR-20260501-1800: species_code+{intake_count+1} per new format
    assert generate_bin_code(species_code, intake_count, finder_name, bin_num) == expected

def test_bin_code_with_special_characters():  # CR-20260501-1800: Renamed test
    # Cleaning check with apostrophes, hyphens, periods preserved
    species_code = "MK"
    intake_count = 5
    finder_name = "O'Malley-Smith"
    bin_num = 2
    
    # CR-20260501-1800: Now preserves apostrophes, hyphens, periods
    expected = "MK6-O'MALLEY-SMITH-2"
    assert generate_bin_code(species_code, intake_count, finder_name, bin_num) == expected

def test_bin_code_with_numbers_in_name():  # CR-20260501-1800: Renamed test
    species_code = "SN"
    intake_count = 1
    finder_name = "Unit 404"
    bin_num = 3
    
    expected = "SN2-UNIT404-3"  # CR-20260501-1800: species_code+{intake_count+1}
    assert generate_bin_code(species_code, intake_count, finder_name, bin_num) == expected

if __name__ == "__main__":
    pytest.main([__file__])
