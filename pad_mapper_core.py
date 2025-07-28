#!/usr/bin/env python3
"""
Core functionality for the Pad to Pin Number Mapping Tool
This module contains the core logic without GUI dependencies
"""

import json
import csv
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PinMapping:
    """Data class for pin mapping information"""
    pad_number: str
    pin_number: str
    signal_name: str = ""
    pin_type: str = ""  # INPUT, OUTPUT, BIDIRECTIONAL, POWER, etc.
    description: str = ""

class PadPinMapperCore:
    """Core functionality class for pad to pin number mapping (no GUI)"""
    
    def __init__(self):
        """Initialize the core mapper"""
        self.mappings: List[PinMapping] = []
        self.current_file = None
    
    def add_mapping(self, pad_number: str, pin_number: str, signal_name: str = "",
                   pin_type: str = "", description: str = "") -> bool:
        """
        Add a new mapping
        
        Args:
            pad_number: The pad identifier
            pin_number: The pin identifier
            signal_name: Optional signal name
            pin_type: Optional pin type
            description: Optional description
            
        Returns:
            True if successful, False if duplicate pad exists
        """
        # Check for duplicate pad numbers
        for mapping in self.mappings:
            if mapping.pad_number == pad_number:
                return False
        
        new_mapping = PinMapping(
            pad_number=pad_number,
            pin_number=pin_number,
            signal_name=signal_name,
            pin_type=pin_type,
            description=description
        )
        
        self.mappings.append(new_mapping)
        return True
    
    def remove_mapping(self, pad_number: str) -> bool:
        """
        Remove a mapping by pad number
        
        Args:
            pad_number: The pad number to remove
            
        Returns:
            True if removed, False if not found
        """
        original_count = len(self.mappings)
        self.mappings = [m for m in self.mappings if m.pad_number != pad_number]
        return len(self.mappings) < original_count
    
    def update_mapping(self, old_pad: str, pad_number: str, pin_number: str,
                      signal_name: str = "", pin_type: str = "", description: str = "") -> bool:
        """
        Update an existing mapping
        
        Args:
            old_pad: The current pad number to update
            pad_number: New pad number
            pin_number: New pin number
            signal_name: New signal name
            pin_type: New pin type
            description: New description
            
        Returns:
            True if successful, False if not found
        """
        for i, mapping in enumerate(self.mappings):
            if mapping.pad_number == old_pad:
                self.mappings[i] = PinMapping(
                    pad_number=pad_number,
                    pin_number=pin_number,
                    signal_name=signal_name,
                    pin_type=pin_type,
                    description=description
                )
                return True
        return False
    
    def get_mapping(self, pad_number: str) -> Optional[PinMapping]:
        """
        Get a mapping by pad number
        
        Args:
            pad_number: The pad number to find
            
        Returns:
            PinMapping object if found, None otherwise
        """
        for mapping in self.mappings:
            if mapping.pad_number == pad_number:
                return mapping
        return None
    
    def search_mappings(self, search_term: str) -> List[PinMapping]:
        """
        Search mappings by term
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching mappings
        """
        search_term = search_term.lower()
        results = []
        
        for mapping in self.mappings:
            if (search_term in mapping.pad_number.lower() or
                search_term in mapping.pin_number.lower() or
                search_term in mapping.signal_name.lower() or
                search_term in mapping.pin_type.lower() or
                search_term in mapping.description.lower()):
                results.append(mapping)
        
        return results
    
    def load_from_json(self, filename: str) -> bool:
        """
        Load mappings from JSON file
        
        Args:
            filename: Path to JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.mappings.clear()
            for item in data.get('mappings', []):
                mapping = PinMapping(**item)
                self.mappings.append(mapping)
            
            self.current_file = filename
            return True
            
        except Exception:
            return False
    
    def save_to_json(self, filename: str) -> bool:
        """
        Save mappings to JSON file
        
        Args:
            filename: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'version': '1.0',
                    'tool': 'Pad to Pin Mapper'
                },
                'mappings': [asdict(mapping) for mapping in self.mappings]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.current_file = filename
            return True
            
        except Exception:
            return False
    
    def export_to_csv(self, filename: str) -> bool:
        """
        Export mappings to CSV file
        
        Args:
            filename: Path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Pad Number', 'Pin Number', 'Signal Name', 'Pin Type', 'Description'])
                
                for mapping in self.mappings:
                    writer.writerow([
                        mapping.pad_number,
                        mapping.pin_number,
                        mapping.signal_name,
                        mapping.pin_type,
                        mapping.description
                    ])
            
            return True
            
        except Exception:
            return False
    
    def import_from_csv(self, filename: str) -> bool:
        """
        Import mappings from CSV file
        
        Args:
            filename: Path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_mappings = []
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:  # At least pad and pin number
                        mapping = PinMapping(
                            pad_number=row[0] if len(row) > 0 else "",
                            pin_number=row[1] if len(row) > 1 else "",
                            signal_name=row[2] if len(row) > 2 else "",
                            pin_type=row[3] if len(row) > 3 else "",
                            description=row[4] if len(row) > 4 else ""
                        )
                        new_mappings.append(mapping)
            
            self.mappings = new_mappings
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about current mappings
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_mappings': len(self.mappings),
            'pin_types': {}
        }
        
        for mapping in self.mappings:
            pin_type = mapping.pin_type or "Unspecified"
            stats['pin_types'][pin_type] = stats['pin_types'].get(pin_type, 0) + 1
        
        return stats
    
    def clear_mappings(self):
        """Clear all mappings"""
        self.mappings.clear()
        self.current_file = None
    
    def get_all_mappings(self) -> List[PinMapping]:
        """Get all mappings"""
        return self.mappings.copy()
    
    def get_mapping_count(self) -> int:
        """Get the number of mappings"""
        return len(self.mappings)