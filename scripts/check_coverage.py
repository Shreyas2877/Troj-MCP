#!/usr/bin/env python3
"""
Check that all files have at least 60% coverage.
"""

import xml.etree.ElementTree as ET
import sys
from pathlib import Path


def check_coverage_per_file(coverage_xml_path: str, min_coverage: float = 55.0):
    """Check that each file has at least min_coverage% coverage."""
    if not Path(coverage_xml_path).exists():
        print(f"❌ Coverage file not found: {coverage_xml_path}")
        return False
    
    # Parse coverage XML
    tree = ET.parse(coverage_xml_path)
    root = tree.getroot()
    
    failed_files = []
    passed_files = []
    
    for package in root.findall('.//package'):
        for class_elem in package.findall('.//class'):
            filename = class_elem.get('filename')
            line_rate = float(class_elem.get('line-rate', 0))
            coverage_percent = line_rate * 100
            
            if coverage_percent < min_coverage:
                failed_files.append((filename, coverage_percent))
            else:
                passed_files.append((filename, coverage_percent))
    
    # Print results
    print(f"📊 Coverage Report (Minimum: {min_coverage}%)")
    print("=" * 50)
    
    if passed_files:
        print(f"✅ Files with coverage ≥ {min_coverage}%:")
        for filename, coverage in sorted(passed_files):
            print(f"  {filename}: {coverage:.1f}%")
        print()
    
    if failed_files:
        print(f"❌ Files with coverage < {min_coverage}%:")
        for filename, coverage in sorted(failed_files):
            print(f"  {filename}: {coverage:.1f}%")
        print()
        return False
    else:
        print(f"🎉 All files have coverage ≥ {min_coverage}%!")
        return True


def main():
    """Main function."""
    coverage_file = "coverage.xml"
    min_coverage = 55.0
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        coverage_file = sys.argv[1]
    if len(sys.argv) > 2:
        min_coverage = float(sys.argv[2])
    
    success = check_coverage_per_file(coverage_file, min_coverage)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
