#!/usr/bin/env python3
"""
Simple test script for the Pad to Pin Mapper
Tests basic functionality without GUI
"""

import sys
import os
import json
from dataclasses import asdict

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pad_pin_mapper import PinMapping
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

def test_pin_mapping():
    """Test PinMapping data class"""
    print("Testing PinMapping data class...")
    
    mapping = PinMapping("A1", "1", "VCC", "POWER", "Power supply")
    assert mapping.pad_number == "A1"
    assert mapping.pin_number == "1"
    assert mapping.signal_name == "VCC"
    assert mapping.pin_type == "POWER"
    assert mapping.description == "Power supply"
    
    # Test serialization
    mapping_dict = asdict(mapping)
    assert isinstance(mapping_dict, dict)
    assert mapping_dict["pad_number"] == "A1"
    
    print("✓ PinMapping tests passed")

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

def test_file_operations():
    """Test file save/load operations"""
    print("Testing file operations...")
    
    # Create test mappings
    mappings = [
        PinMapping("A1", "1", "VCC", "POWER", "Power supply"),
        PinMapping("A2", "2", "GND", "GROUND", "Ground"),
    ]
    
    # Test JSON serialization
    data = {
        'metadata': {
            'created': '2024-01-01T12:00:00',
            'version': '1.0',
            'tool': 'Pad to Pin Mapper Test'
        },
        'mappings': [asdict(mapping) for mapping in mappings]
    }
    
    # Save to test file
    test_file = "test_mappings.json"
    try:
        with open(test_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Load from test file
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data['mappings']) == 2
        assert loaded_data['mappings'][0]['pad_number'] == "A1"
        
        # Clean up
        os.remove(test_file)
        
        print("✓ File operation tests passed")
        
    except Exception as e:
        print(f"✗ File operation test failed: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run all tests"""
    print("Running Pad to Pin Mapper Tests")
    print("=" * 40)
    
    try:
        test_validation()
        test_pin_mapping()
        test_utility_functions()
        test_file_operations()
        
        print("=" * 40)
        print("✓ All tests passed!")
        return 0
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())