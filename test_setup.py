#!/usr/bin/env python3
"""
Pre-Deployment Test Script
Run this before deploying to verify everything is set up correctly
"""

import sys
import os

def test_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and 8 <= version.minor <= 11:
        print("  ✅ Python version is compatible")
        return True
    else:
        print("  ⚠️  Warning: Recommended Python 3.8-3.11")
        return False

def test_required_packages():
    """Check if required packages are installed"""
    required = ['streamlit', 'pandas', 'plotly', 'numpy']
    missing = []
    
    print("\n✓ Checking Required Packages:")
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package} - installed")
        except ImportError:
            print(f"  ❌ {package} - NOT FOUND")
            missing.append(package)
    
    if missing:
        print(f"\n  ⚠️  Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    return True

def test_csv_files():
    """Check if all required CSV files exist"""
    required_files = [
        'pune_citizen_grievances.csv',
        'pune_energy_consumption.csv',
        'pune_traffic_flow.csv',
        'pune_waste_management.csv'
    ]
    
    print("\n✓ Checking Data Files:")
    missing = []
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            print(f"  ✅ {file} - {size:.1f} KB")
        else:
            print(f"  ❌ {file} - NOT FOUND")
            missing.append(file)
    
    if missing:
        print(f"\n  ⚠️  Missing files: {', '.join(missing)}")
        return False
    return True

def test_csv_format():
    """Verify CSV file format"""
    print("\n✓ Checking CSV Format:")
    try:
        import pandas as pd
        
        files_columns = {
            'pune_citizen_grievances.csv': ['Date', 'Zone_Name', 'Ticket_ID', 'Department', 'Issue_Type', 'Status', 'SLA_Days'],
            'pune_energy_consumption.csv': ['Date', 'Hour', 'Zone_Name', 'Feeder_ID', 'Energy_Consumption_kWh', 'Grid_Voltage', 'Power_Cut_Flag'],
            'pune_traffic_flow.csv': ['Date', 'Hour', 'Zone_Name', 'Junction_ID', 'Vehicle_Volume', 'Avg_Speed_Kmph', 'Congestion_Index'],
            'pune_waste_management.csv': ['Date', 'Zone_Name', 'Total_Waste_Collected_Kg', 'Avg_Bin_Fill_Level_Percent', 'Segregation_Efficiency_Percent', 'Missed_Pickups']
        }
        
        all_valid = True
        for file, expected_cols in files_columns.items():
            if os.path.exists(file):
                df = pd.read_csv(file, nrows=5)
                actual_cols = df.columns.tolist()
                
                if set(expected_cols) == set(actual_cols):
                    print(f"  ✅ {file} - {len(df.columns)} columns, {len(pd.read_csv(file)):,} rows")
                else:
                    print(f"  ⚠️  {file} - Column mismatch")
                    print(f"     Expected: {expected_cols}")
                    print(f"     Found: {actual_cols}")
                    all_valid = False
        
        return all_valid
    except Exception as e:
        print(f"  ❌ Error checking CSV format: {str(e)}")
        return False

def test_app_file():
    """Check if app.py exists and is valid"""
    print("\n✓ Checking Application File:")
    if os.path.exists('app.py'):
        size = os.path.getsize('app.py') / 1024  # KB
        print(f"  ✅ app.py - {size:.1f} KB")
        
        # Check for syntax errors
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                compile(f.read(), 'app.py', 'exec')
            print("  ✅ No syntax errors detected")
            return True
        except SyntaxError as e:
            print(f"  ❌ Syntax error in app.py: {e}")
            return False
    else:
        print("  ❌ app.py - NOT FOUND")
        return False

def test_config_file():
    """Check if Streamlit config exists"""
    print("\n✓ Checking Configuration:")
    if os.path.exists('.streamlit/config.toml'):
        print("  ✅ .streamlit/config.toml - found")
        return True
    else:
        print("  ⚠️  .streamlit/config.toml - not found (optional)")
        return True

def test_requirements_file():
    """Check if requirements.txt exists"""
    print("\n✓ Checking Requirements File:")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
        print(f"  ✅ requirements.txt - {len(lines)} packages listed")
        for line in lines:
            print(f"     - {line}")
        return True
    else:
        print("  ❌ requirements.txt - NOT FOUND")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🔍 PRE-DEPLOYMENT VERIFICATION")
    print("="*60)
    
    tests = [
        test_python_version,
        test_required_packages,
        test_csv_files,
        test_csv_format,
        test_app_file,
        test_requirements_file,
        test_config_file
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 You're ready to deploy!")
        print("\nNext steps:")
        print("1. Test locally: streamlit run app.py")
        print("2. Push to GitHub")
        print("3. Deploy on Streamlit Cloud")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n🔧 Please fix the issues above before deploying")
    
    print("="*60)

if __name__ == "__main__":
    main()