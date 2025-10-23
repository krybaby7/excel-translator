"""
Quick test script to verify everything is working
Run this first before running the full test suite
"""
import os
import sys

# Fix Unicode display on Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    required_packages = [
        'openpyxl',
        'xlrd',
        'xlwt',
        'deep_translator',
        'flask',
        'pytest'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✓ All dependencies installed\n")
    return True


def check_directories():
    """Check if required directories exist"""
    print("Checking directories...")
    directories = ['tests', 'test_data', 'test_results']

    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - MISSING")
            all_exist = False

    if not all_exist:
        print("\n❌ Some directories are missing")
        return False

    print("✓ All directories present\n")
    return True


def check_test_data():
    """Check if test data files exist"""
    print("Checking test data...")
    test_files = [
        'simple_french.xlsx',
        'formatted_french.xlsx',
        'multi_sheet_french.xlsx',
        'large_french.xlsx',
        'old_format.xls'
    ]

    missing = []
    for test_file in test_files:
        path = os.path.join('test_data', test_file)
        if os.path.exists(path):
            print(f"  ✓ {test_file}")
        else:
            print(f"  ✗ {test_file} - MISSING")
            missing.append(test_file)

    if missing:
        print(f"\n❌ Missing test files: {len(missing)}")
        print("Run: python generate_test_data.py")
        return False

    print("✓ All test data files present\n")
    return True


def run_quick_test():
    """Run a quick functional test"""
    print("Running quick functional test...")

    try:
        from excel_translator import translate_excel_with_format

        input_file = "test_data/simple_french.xlsx"
        output_file = "test_results/quick_test_output.xlsx"

        print(f"  Testing translation: {input_file}")
        translate_excel_with_format(input_file, output_file, "fr", "en")

        if os.path.exists(output_file):
            print("  ✓ Translation successful")
            print(f"  ✓ Output file created: {output_file}")

            # Cleanup
            os.remove(output_file)
            print("  ✓ Cleanup complete")
            print("✓ Quick test passed!\n")
            return True
        else:
            print("  ✗ Output file not created")
            return False

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def main():
    """Run all quick checks"""
    print("\n" + "="*70)
    print("  EXCEL TRANSLATOR - QUICK VERIFICATION")
    print("="*70 + "\n")

    checks = [
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Test Data", check_test_data),
        ("Functional Test", run_quick_test),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed with error: {str(e)}\n")
            results.append((name, False))

    # Summary
    print("="*70)
    print("  SUMMARY")
    print("="*70)

    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:30} {status}")
        if not result:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n✓ All quick checks passed!")
        print("\nNext steps:")
        print("  1. Review TESTING_GUIDE.md for detailed testing info")
        print("  2. Run full test suite: python run_tests.py")
        print("  3. Review results and fix any issues")
        print("  4. Proceed with Supabase backend integration")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Missing packages: pip install -r requirements.txt")
        print("  • Missing test data: python generate_test_data.py")
        print("  • Missing directories: mkdir tests test_data test_results")
        return 1


if __name__ == "__main__":
    sys.exit(main())
