#!/usr/bin/env python3
"""
Pad to Pin Number Mapping Tool
A Visual Studio Code compatible tool for mapping IC pad numbers to pin numbers
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
    
class PadPinMapper:
    """Main application class for pad to pin number mapping"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Pad to Pin Number Mapping Tool")
        self.root.geometry("1000x700")
        
        # Data storage
        self.mappings: List[PinMapping] = []
        self.current_file = None
        
        self.setup_ui()
        self.load_default_mappings()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Pad to Pin Number Mapping Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar, text="New", command=self.new_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save As", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Treeview for mappings
        self.tree = ttk.Treeview(content_frame, columns=("pad", "pin", "signal", "type", "description"), 
                                show="headings", height=15)
        
        # Define columns
        self.tree.heading("pad", text="Pad Number")
        self.tree.heading("pin", text="Pin Number")
        self.tree.heading("signal", text="Signal Name")
        self.tree.heading("type", text="Pin Type")
        self.tree.heading("description", text="Description")
        
        # Column widths
        self.tree.column("pad", width=100)
        self.tree.column("pin", width=100)
        self.tree.column("signal", width=150)
        self.tree.column("type", width=120)
        self.tree.column("description", width=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(content_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Entry form
        entry_frame = ttk.LabelFrame(main_frame, text="Add/Edit Mapping", padding="10")
        entry_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Entry fields
        ttk.Label(entry_frame, text="Pad Number:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.pad_var = tk.StringVar()
        self.pad_entry = ttk.Entry(entry_frame, textvariable=self.pad_var, width=15)
        self.pad_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(entry_frame, text="Pin Number:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.pin_var = tk.StringVar()
        self.pin_entry = ttk.Entry(entry_frame, textvariable=self.pin_var, width=15)
        self.pin_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(entry_frame, text="Signal Name:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.signal_var = tk.StringVar()
        self.signal_entry = ttk.Entry(entry_frame, textvariable=self.signal_var, width=15)
        self.signal_entry.grid(row=1, column=1, padx=(0, 10))
        
        ttk.Label(entry_frame, text="Pin Type:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(entry_frame, textvariable=self.type_var, width=12,
                                      values=["INPUT", "OUTPUT", "BIDIRECTIONAL", "POWER", "GROUND", "NC"])
        self.type_combo.grid(row=1, column=3, padx=(0, 10))
        
        ttk.Label(entry_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(entry_frame, textvariable=self.desc_var, width=50)
        self.desc_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(button_frame, text="Add", command=self.add_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self.delete_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=(0, 5))
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="5")
        search_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).grid(row=0, column=2)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_item_select)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_default_mappings(self):
        """Load some default mappings as examples"""
        default_mappings = [
            PinMapping("A1", "1", "VCC", "POWER", "Power supply"),
            PinMapping("A2", "2", "GND", "GROUND", "Ground"),
            PinMapping("B1", "3", "CLK", "INPUT", "Clock input"),
            PinMapping("B2", "4", "DATA", "BIDIRECTIONAL", "Data line"),
            PinMapping("C1", "5", "EN", "INPUT", "Enable signal"),
            PinMapping("C2", "6", "OUT", "OUTPUT", "Output signal"),
        ]
        
        for mapping in default_mappings:
            self.mappings.append(mapping)
        
        self.refresh_tree()
    
    def refresh_tree(self):
        """Refresh the treeview with current mappings"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current mappings
        for mapping in self.mappings:
            self.tree.insert("", "end", values=(
                mapping.pad_number,
                mapping.pin_number,
                mapping.signal_name,
                mapping.pin_type,
                mapping.description
            ))
        
        self.status_var.set(f"Loaded {len(self.mappings)} mappings")
    
    def add_mapping(self):
        """Add a new mapping"""
        if not self.pad_var.get() or not self.pin_var.get():
            messagebox.showerror("Error", "Pad number and pin number are required!")
            return
        
        # Check for duplicate pad numbers
        for mapping in self.mappings:
            if mapping.pad_number == self.pad_var.get():
                messagebox.showerror("Error", f"Pad number {self.pad_var.get()} already exists!")
                return
        
        new_mapping = PinMapping(
            pad_number=self.pad_var.get(),
            pin_number=self.pin_var.get(),
            signal_name=self.signal_var.get(),
            pin_type=self.type_var.get(),
            description=self.desc_var.get()
        )
        
        self.mappings.append(new_mapping)
        self.refresh_tree()
        self.clear_form()
        self.status_var.set(f"Added mapping for pad {new_mapping.pad_number}")
    
    def update_mapping(self):
        """Update selected mapping"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mapping to update!")
            return
        
        if not self.pad_var.get() or not self.pin_var.get():
            messagebox.showerror("Error", "Pad number and pin number are required!")
            return
        
        # Get the selected item's values
        item = self.tree.item(selected[0])
        old_pad = item['values'][0]
        
        # Find and update the mapping
        for i, mapping in enumerate(self.mappings):
            if mapping.pad_number == old_pad:
                self.mappings[i] = PinMapping(
                    pad_number=self.pad_var.get(),
                    pin_number=self.pin_var.get(),
                    signal_name=self.signal_var.get(),
                    pin_type=self.type_var.get(),
                    description=self.desc_var.get()
                )
                break
        
        self.refresh_tree()
        self.clear_form()
        self.status_var.set(f"Updated mapping for pad {self.pad_var.get()}")
    
    def delete_mapping(self):
        """Delete selected mapping"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mapping to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this mapping?"):
            item = self.tree.item(selected[0])
            pad_to_delete = item['values'][0]
            
            self.mappings = [m for m in self.mappings if m.pad_number != pad_to_delete]
            self.refresh_tree()
            self.clear_form()
            self.status_var.set(f"Deleted mapping for pad {pad_to_delete}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.pad_var.set("")
        self.pin_var.set("")
        self.signal_var.set("")
        self.type_var.set("")
        self.desc_var.set("")
    
    def on_item_select(self, event):
        """Handle item selection in treeview"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            
            self.pad_var.set(values[0])
            self.pin_var.set(values[1])
            self.signal_var.set(values[2])
            self.type_var.set(values[3])
            self.desc_var.set(values[4])
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_var.get().lower()
        
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display matching mappings
        filtered_mappings = []
        for mapping in self.mappings:
            if (search_term in mapping.pad_number.lower() or
                search_term in mapping.pin_number.lower() or
                search_term in mapping.signal_name.lower() or
                search_term in mapping.pin_type.lower() or
                search_term in mapping.description.lower()):
                filtered_mappings.append(mapping)
        
        # Add filtered mappings to tree
        for mapping in filtered_mappings:
            self.tree.insert("", "end", values=(
                mapping.pad_number,
                mapping.pin_number,
                mapping.signal_name,
                mapping.pin_type,
                mapping.description
            ))
        
        self.status_var.set(f"Found {len(filtered_mappings)} matching mappings")
    
    def clear_search(self):
        """Clear search and show all mappings"""
        self.search_var.set("")
        self.refresh_tree()
    
    def new_mapping(self):
        """Create new mapping file"""
        if self.mappings and messagebox.askyesno("Confirm", "Clear current mappings and start new?"):
            self.mappings.clear()
            self.refresh_tree()
            self.current_file = None
            self.status_var.set("New mapping file created")
    
    def open_file(self):
        """Open mapping file"""
        filename = filedialog.askopenfilename(
            title="Open Mapping File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.mappings.clear()
                for item in data.get('mappings', []):
                    mapping = PinMapping(**item)
                    self.mappings.append(mapping)
                
                self.refresh_tree()
                self.current_file = filename
                self.status_var.set(f"Opened {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save current mapping file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save mapping file with new name"""
        filename = filedialog.asksaveasfilename(
            title="Save Mapping File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
    
    def _save_to_file(self, filename):
        """Internal method to save to file"""
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
            
            self.status_var.set(f"Saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def export_csv(self):
        """Export mappings to CSV"""
        filename = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
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
                
                self.status_var.set(f"Exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def import_csv(self):
        """Import mappings from CSV"""
        filename = filedialog.askopenfilename(
            title="Import from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
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
                
                if messagebox.askyesno("Confirm", f"Import {len(new_mappings)} mappings? This will replace current mappings."):
                    self.mappings = new_mappings
                    self.refresh_tree()
                    self.status_var.set(f"Imported {len(new_mappings)} mappings from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = PadPinMapper(root)
    root.mainloop()

if __name__ == "__main__":
    main()