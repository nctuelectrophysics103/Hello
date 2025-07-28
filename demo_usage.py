#!/usr/bin/env python3
"""
Demo script showing how to use the Pad to Pin Mapper tool
"""

from pad_mapper_core import PadPinMapperCore
from pin_mapper_utils import generate_pin_mapping_report, export_to_text_format

def create_sample_ic_mapping():
    """Create a sample IC mapping demonstrating typical usage"""
    print("Creating sample IC mapping...")
    
    # Initialize the mapper
    mapper = PadPinMapperCore()
    
    # Add power pins
    mapper.add_mapping("A1", "1", "VDD", "POWER", "3.3V Power Supply")
    mapper.add_mapping("A8", "8", "GND", "GROUND", "Ground")
    mapper.add_mapping("H1", "64", "VDD", "POWER", "3.3V Power Supply")
    mapper.add_mapping("H8", "57", "GND", "GROUND", "Ground")
    
    # Add clock signals
    mapper.add_mapping("B2", "9", "CLK", "INPUT", "Main system clock")
    mapper.add_mapping("B3", "10", "CLK_OUT", "OUTPUT", "Generated clock output")
    
    # Add data bus
    for i in range(8):
        pad = f"C{i+1}"
        pin = str(16 + i)
        signal = f"DATA{i}"
        mapper.add_mapping(pad, pin, signal, "BIDIRECTIONAL", f"Data bus bit {i}")
    
    # Add address bus
    for i in range(4):
        pad = f"D{i+1}"
        pin = str(24 + i)
        signal = f"ADDR{i}"
        mapper.add_mapping(pad, pin, signal, "INPUT", f"Address bus bit {i}")
    
    # Add control signals
    mapper.add_mapping("E1", "32", "RESET_N", "INPUT", "Active low reset")
    mapper.add_mapping("E2", "33", "ENABLE", "INPUT", "Chip enable")
    mapper.add_mapping("E3", "34", "WR_N", "INPUT", "Active low write enable")
    mapper.add_mapping("E4", "35", "RD_N", "INPUT", "Active low read enable")
    
    # Add GPIO pins
    for i in range(8):
        pad = f"F{i+1}"
        pin = str(40 + i)
        signal = f"GPIO{i}"
        mapper.add_mapping(pad, pin, signal, "BIDIRECTIONAL", f"General purpose I/O {i}")
    
    # Add analog pins
    mapper.add_mapping("G1", "48", "VREF", "INPUT", "Analog reference voltage")
    mapper.add_mapping("G2", "49", "ADC_IN", "INPUT", "Analog to digital converter input")
    mapper.add_mapping("G3", "50", "DAC_OUT", "OUTPUT", "Digital to analog converter output")
    
    return mapper

def demonstrate_features():
    """Demonstrate the various features of the tool"""
    print("=== Pad to Pin Mapper Demo ===\n")
    
    # Create sample mapping
    mapper = create_sample_ic_mapping()
    
    print(f"Created mapping with {mapper.get_mapping_count()} pin assignments\n")
    
    # Show statistics
    stats = mapper.get_statistics()
    print("Pin Type Statistics:")
    for pin_type, count in stats['pin_types'].items():
        print(f"  {pin_type}: {count}")
    print()
    
    # Demonstrate search functionality
    print("Searching for 'CLK' signals:")
    clk_results = mapper.search_mappings("CLK")
    for result in clk_results:
        print(f"  {result.pad_number} -> {result.pin_number}: {result.signal_name}")
    print()
    
    print("Searching for 'POWER' type pins:")
    power_results = mapper.search_mappings("POWER")
    for result in power_results:
        print(f"  {result.pad_number} -> {result.pin_number}: {result.signal_name} ({result.pin_type})")
    print()
    
    # Demonstrate getting specific mappings
    print("Getting specific mapping for pad A1:")
    a1_mapping = mapper.get_mapping("A1")
    if a1_mapping:
        print(f"  Pad A1 -> Pin {a1_mapping.pin_number}: {a1_mapping.signal_name}")
        print(f"  Type: {a1_mapping.pin_type}")
        print(f"  Description: {a1_mapping.description}")
    print()
    
    # Save to files
    print("Saving to JSON format...")
    mapper.save_to_json("sample_ic_mapping.json")
    print("✓ Saved to sample_ic_mapping.json")
    
    print("Exporting to CSV format...")
    mapper.export_to_csv("sample_ic_mapping.csv")
    print("✓ Exported to sample_ic_mapping.csv")
    
    # Generate reports
    print("\nGenerating text report...")
    report = generate_pin_mapping_report(mapper.get_all_mappings())
    
    # Save report to file
    with open("sample_ic_report.txt", "w") as f:
        f.write(report)
    print("✓ Report saved to sample_ic_report.txt")
    
    # Show summary of first few mappings
    print("\nFirst 5 mappings (sorted by pad):")
    all_mappings = mapper.get_all_mappings()
    sorted_mappings = sorted(all_mappings, key=lambda x: x.pad_number)
    
    for mapping in sorted_mappings[:5]:
        print(f"  {mapping.pad_number:4} -> {mapping.pin_number:3}: {mapping.signal_name:12} ({mapping.pin_type})")
    
    if len(sorted_mappings) > 5:
        print(f"  ... and {len(sorted_mappings) - 5} more mappings")
    
    print(f"\nDemo completed! Generated files:")
    print("  - sample_ic_mapping.json (JSON format)")
    print("  - sample_ic_mapping.csv (CSV format)")
    print("  - sample_ic_report.txt (Text report)")
    print("\nYou can open these files in VS Code to examine the data formats.")

def main():
    """Main demo function"""
    try:
        demonstrate_features()
        return 0
    except Exception as e:
        print(f"Demo failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())