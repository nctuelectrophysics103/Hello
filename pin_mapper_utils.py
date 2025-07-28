#!/usr/bin/env python3
"""
Utility functions for the Pad to Pin Number Mapping Tool
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

def validate_pad_number(pad_number: str) -> ValidationResult:
    """
    Validate pad number format
    
    Args:
        pad_number: The pad number to validate
        
    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []
    
    if not pad_number:
        errors.append("Pad number cannot be empty")
        return ValidationResult(False, errors, warnings)
    
    # Check for valid alphanumeric format (e.g., A1, B12, AA1)
    if not re.match(r'^[A-Za-z]+\d+$', pad_number):
        errors.append("Pad number should be in format like A1, B12, AA1")
    
    # Check length
    if len(pad_number) > 10:
        warnings.append("Pad number is unusually long")
    
    return ValidationResult(len(errors) == 0, errors, warnings)

def validate_pin_number(pin_number: str) -> ValidationResult:
    """
    Validate pin number format
    
    Args:
        pin_number: The pin number to validate
        
    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []
    
    if not pin_number:
        errors.append("Pin number cannot be empty")
        return ValidationResult(False, errors, warnings)
    
    # Check if it's a valid number or alphanumeric
    if not re.match(r'^[A-Za-z]*\d+[A-Za-z]*$', pin_number):
        errors.append("Pin number should contain at least one digit")
    
    # Check for reasonable range
    try:
        # Extract numeric part
        numeric_part = re.findall(r'\d+', pin_number)
        if numeric_part:
            num = int(numeric_part[0])
            if num <= 0:
                errors.append("Pin number should be positive")
            elif num > 1000:
                warnings.append("Pin number seems unusually high")
    except ValueError:
        pass  # Already handled by regex check
    
    return ValidationResult(len(errors) == 0, errors, warnings)

def validate_signal_name(signal_name: str) -> ValidationResult:
    """
    Validate signal name format
    
    Args:
        signal_name: The signal name to validate
        
    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []
    
    if signal_name:
        # Check for valid identifier format
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', signal_name):
            warnings.append("Signal name should follow identifier conventions (letters, numbers, underscore)")
        
        # Check length
        if len(signal_name) > 50:
            warnings.append("Signal name is very long")
    
    return ValidationResult(True, errors, warnings)  # Signal name is optional

def generate_pin_mapping_report(mappings: List) -> str:
    """
    Generate a text report of pin mappings
    
    Args:
        mappings: List of PinMapping objects
        
    Returns:
        Formatted text report
    """
    if not mappings:
        return "No mappings to report"
    
    report_lines = [
        "PAD TO PIN MAPPING REPORT",
        "=" * 50,
        f"Total mappings: {len(mappings)}",
        "",
        "Mapping Details:",
        "-" * 30
    ]
    
    # Sort mappings by pad number for better readability
    sorted_mappings = sorted(mappings, key=lambda x: (
        re.findall(r'[A-Za-z]+', x.pad_number)[0] if re.findall(r'[A-Za-z]+', x.pad_number) else '',
        int(re.findall(r'\d+', x.pad_number)[0]) if re.findall(r'\d+', x.pad_number) else 0
    ))
    
    for mapping in sorted_mappings:
        report_lines.extend([
            f"Pad: {mapping.pad_number:8} -> Pin: {mapping.pin_number:8}",
            f"  Signal: {mapping.signal_name or 'N/A':15} Type: {mapping.pin_type or 'N/A'}",
            f"  Description: {mapping.description or 'N/A'}",
            ""
        ])
    
    # Add statistics
    pin_types = {}
    for mapping in mappings:
        pin_type = mapping.pin_type or "Unspecified"
        pin_types[pin_type] = pin_types.get(pin_type, 0) + 1
    
    if pin_types:
        report_lines.extend([
            "Pin Type Statistics:",
            "-" * 20
        ])
        for pin_type, count in sorted(pin_types.items()):
            report_lines.append(f"{pin_type:15}: {count:3}")
    
    return "\n".join(report_lines)

def detect_mapping_conflicts(mappings: List) -> Dict[str, List]:
    """
    Detect conflicts in pin mappings
    
    Args:
        mappings: List of PinMapping objects
        
    Returns:
        Dictionary with conflict types and affected mappings
    """
    conflicts = {
        'duplicate_pads': [],
        'duplicate_pins': [],
        'duplicate_signals': []
    }
    
    # Track seen values
    seen_pads = {}
    seen_pins = {}
    seen_signals = {}
    
    for i, mapping in enumerate(mappings):
        # Check for duplicate pad numbers
        if mapping.pad_number in seen_pads:
            conflicts['duplicate_pads'].extend([
                seen_pads[mapping.pad_number],
                i
            ])
        else:
            seen_pads[mapping.pad_number] = i
        
        # Check for duplicate pin numbers
        if mapping.pin_number in seen_pins:
            conflicts['duplicate_pins'].extend([
                seen_pins[mapping.pin_number],
                i
            ])
        else:
            seen_pins[mapping.pin_number] = i
        
        # Check for duplicate signal names (if not empty)
        if mapping.signal_name and mapping.signal_name in seen_signals:
            conflicts['duplicate_signals'].extend([
                seen_signals[mapping.signal_name],
                i
            ])
        elif mapping.signal_name:
            seen_signals[mapping.signal_name] = i
    
    # Remove duplicates from conflict lists
    for key in conflicts:
        conflicts[key] = list(set(conflicts[key]))
    
    return conflicts

def suggest_pin_number(pad_number: str, existing_mappings: List) -> Optional[str]:
    """
    Suggest a pin number based on pad number and existing mappings
    
    Args:
        pad_number: The pad number to suggest a pin for
        existing_mappings: List of existing PinMapping objects
        
    Returns:
        Suggested pin number or None
    """
    if not pad_number:
        return None
    
    # Extract existing pin numbers
    used_pins = set()
    for mapping in existing_mappings:
        try:
            # Extract numeric part of pin number
            pin_nums = re.findall(r'\d+', mapping.pin_number)
            if pin_nums:
                used_pins.add(int(pin_nums[0]))
        except (ValueError, IndexError):
            pass
    
    # Find next available pin number
    suggested_pin = 1
    while suggested_pin in used_pins:
        suggested_pin += 1
    
    return str(suggested_pin)

def export_to_text_format(mappings: List, format_type: str = "table") -> str:
    """
    Export mappings to various text formats
    
    Args:
        mappings: List of PinMapping objects
        format_type: Type of format ("table", "list", "markdown")
        
    Returns:
        Formatted text string
    """
    if not mappings:
        return "No mappings to export"
    
    if format_type == "table":
        lines = [
            f"{'Pad':<8} {'Pin':<8} {'Signal':<15} {'Type':<12} {'Description':<30}",
            "-" * 80
        ]
        for mapping in mappings:
            lines.append(
                f"{mapping.pad_number:<8} {mapping.pin_number:<8} "
                f"{mapping.signal_name[:14]:<15} {mapping.pin_type[:11]:<12} "
                f"{mapping.description[:29]:<30}"
            )
    
    elif format_type == "list":
        lines = []
        for i, mapping in enumerate(mappings, 1):
            lines.extend([
                f"{i}. Pad {mapping.pad_number} -> Pin {mapping.pin_number}",
                f"   Signal: {mapping.signal_name or 'N/A'}",
                f"   Type: {mapping.pin_type or 'N/A'}",
                f"   Description: {mapping.description or 'N/A'}",
                ""
            ])
    
    elif format_type == "markdown":
        lines = [
            "| Pad | Pin | Signal | Type | Description |",
            "|-----|-----|--------|------|-------------|"
        ]
        for mapping in mappings:
            lines.append(
                f"| {mapping.pad_number} | {mapping.pin_number} | "
                f"{mapping.signal_name or 'N/A'} | {mapping.pin_type or 'N/A'} | "
                f"{mapping.description or 'N/A'} |"
            )
    
    else:
        return "Unknown format type"
    
    return "\n".join(lines)

def parse_pad_range(pad_range: str) -> List[str]:
    """
    Parse a pad range specification (e.g., "A1-A10" or "B1,B3,B5")
    
    Args:
        pad_range: Range specification string
        
    Returns:
        List of individual pad numbers
    """
    pads = []
    
    # Split by commas first
    parts = [part.strip() for part in pad_range.split(',')]
    
    for part in parts:
        if '-' in part:
            # Handle range (e.g., A1-A10)
            try:
                start, end = part.split('-')
                start = start.strip()
                end = end.strip()
                
                # Extract letter and number parts
                start_match = re.match(r'^([A-Za-z]+)(\d+)$', start)
                end_match = re.match(r'^([A-Za-z]+)(\d+)$', end)
                
                if start_match and end_match:
                    start_letter, start_num = start_match.groups()
                    end_letter, end_num = end_match.groups()
                    
                    if start_letter == end_letter:
                        # Same letter, expand numbers
                        for num in range(int(start_num), int(end_num) + 1):
                            pads.append(f"{start_letter}{num}")
                    else:
                        # Different letters, add both endpoints
                        pads.extend([start, end])
                else:
                    # Invalid range format, add as-is
                    pads.append(part)
            except ValueError:
                # Invalid range, add as-is
                pads.append(part)
        else:
            # Single pad
            pads.append(part)
    
    return pads