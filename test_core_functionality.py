#!/usr/bin/env python3
"""
Test script for core functionality (no GUI dependencies)
"""

import os
import sys
import tempfile
from pad_mapper_core import PadPinMapperCore, PinMapping
from pin_mapper_utils import (
    validate_pad_number,
    validate_pin_number,
    validate_signal_name,
    generate_pin_mapping_report,
    detect_mapping_conflicts,
    suggest_pin_number,
    export_to_text_format,
    parse_pad_range
)

def test_core_functionality():
    """Test the core mapper functionality"""
    print("Testing core functionality...")
    
    mapper = PadPinMapperCore()
    
    # Test adding mappings
    assert mapper.add_mapping("A1", "1", "VCC", "POWER", "Power supply")
    assert mapper.add_mapping("A2", "2", "GND", "GROUND", "Ground")
    assert mapper.add_mapping("B1", "3", "CLK", "INPUT", "Clock input")
    
    # Test duplicate prevention
    assert not mapper.add_mapping("A1", "4", "DUP", "INPUT", "Duplicate")
    
    # Test mapping count
    assert mapper.get_mapping_count() == 3
    
    # Test getting specific mapping
    mapping = mapper.get_mapping("A1")
    assert mapping is not None
    assert mapping.signal_name == "VCC"
    
    # Test search
    results = mapper.search_mappings("VCC")
    assert len(results) == 1
    assert results[0].pad_number == "A1"
    
    # Test update
    assert mapper.update_mapping("A1", "A1", "1", "VDD", "POWER", "Power supply 3.3V")
    updated = mapper.get_mapping("A1")
    assert updated.signal_name == "VDD"
    assert updated.description == "Power supply 3.3V"
    
    # Test remove
    assert mapper.remove_mapping("B1")
    assert mapper.get_mapping_count() == 2
    assert mapper.get_mapping("B1") is None
    
    # Test statistics
    stats = mapper.get_statistics()
    assert stats['total_mappings'] == 2
    assert 'POWER' in stats['pin_types']
    assert 'GROUND' in stats['pin_types']
    
    print("✓ Core functionality tests passed")

def test_file_operations():
    """Test file save/load operations"""
    print("Testing file operations...")
    
    mapper = PadPinMapperCore()
    
    # Add test data
    mapper.add_mapping("A1", "1", "VCC", "POWER", "Power supply")
    mapper.add_mapping("A2", "2", "GND", "GROUND", "Ground")
    
    # Test JSON save/load
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_file = f.name
    
    try:
        assert mapper.save_to_json(json_file)
        
        new_mapper = PadPinMapperCore()
        assert new_mapper.load_from_json(json_file)
        assert new_mapper.get_mapping_count() == 2
        
        mapping = new_mapper.get_mapping("A1")
        assert mapping.signal_name == "VCC"
        
    finally:
        os.unlink(json_file)
    
    # Test CSV export/import
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_file = f.name
    
    try:
        assert mapper.export_to_csv(csv_file)
        
        new_mapper = PadPinMapperCore()
        assert new_mapper.import_from_csv(csv_file)
        assert new_mapper.get_mapping_count() == 2
        
    finally:
        os.unlink(csv_file)
    
    print("✓ File operation tests passed")

def test_validation():
    """Test validation functions"""
    print("Testing validation functions...")
    
    # Test pad number validation
    result = validate_pad_number("A1")
    assert result.is_valid, f"A1 should be valid: {result.errors}"
    
    result = validate_pad_number("123")
    assert not result.is_valid, "123 should be invalid"
    
    result = validate_pad_number("")
    assert not result.is_valid, "Empty string should be invalid"
    
    # Test pin number validation
    result = validate_pin_number("1")
    assert result.is_valid, f"1 should be valid: {result.errors}"
    
    result = validate_pin_number("A1")
    assert result.is_valid, f"A1 should be valid: {result.errors}"
    
    result = validate_pin_number("")
    assert not result.is_valid, "Empty string should be invalid"
    
    # Test signal name validation
    result = validate_signal_name("CLK")
    assert result.is_valid, f"CLK should be valid: {result.errors}"
    
    result = validate_signal_name("")
    assert result.is_valid, "Empty signal name should be valid (optional)"
    
    print("✓ Validation tests passed")

def test_utility_functions():
    """Test utility functions"""
    print("Testing utility functions...")
    
    # Create test mappings
    mappings = [
        PinMapping("A1", "1", "VCC", "POWER", "Power supply"),
        PinMapping("A2", "2", "GND", "GROUND", "Ground"),
        PinMapping("B1", "3", "CLK", "INPUT", "Clock input"),
    ]
    
    # Test report generation
    report = generate_pin_mapping_report(mappings)
    assert "PAD TO PIN MAPPING REPORT" in report
    assert "Total mappings: 3" in report
    
    # Test conflict detection
    conflicts = detect_mapping_conflicts(mappings)
    assert len(conflicts["duplicate_pads"]) == 0
    assert len(conflicts["duplicate_pins"]) == 0
    
    # Test duplicate detection
    duplicate_mappings = mappings + [PinMapping("A1", "4", "DUP", "INPUT", "Duplicate")]
    conflicts = detect_mapping_conflicts(duplicate_mappings)
    assert len(conflicts["duplicate_pads"]) > 0
    
    # Test pin suggestion
    suggested = suggest_pin_number("C1", mappings)
    assert suggested == "4"  # Next available pin
    
    # Test text export
    text_export = export_to_text_format(mappings, "table")
    assert "Pad" in text_export and "Pin" in text_export
    
    # Test pad range parsing
    pads = parse_pad_range("A1-A3")
    assert pads == ["A1", "A2", "A3"]
    
    pads = parse_pad_range("B1,B3,B5")
    assert pads == ["B1", "B3", "B5"]
    
    print("✓ Utility function tests passed")

def main():
    """Run all tests"""
    print("Running Pad to Pin Mapper Core Tests")
    print("=" * 50)
    
    try:
        test_core_functionality()
        test_file_operations()
        test_validation()
        test_utility_functions()
        
        print("=" * 50)
        print("✓ All core tests passed!")
        print("\nThe pad to pin mapper tool is working correctly.")
        print("You can now use it in Visual Studio Code:")
        print("1. Open this project in VS Code")
        print("2. Press F5 to run with debugging")
        print("3. Or use Ctrl+Shift+P -> 'Tasks: Run Task' -> 'Run Pad Pin Mapper'")
        print("\nNote: GUI functionality requires tkinter to be installed.")
        return 0
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())