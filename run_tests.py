"""
Convenience script to run all tests with detailed reporting
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print('='*70)
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    """Run all test suites"""
    print("\n" + "="*70)
    print("  EXCEL TRANSLATOR - COMPREHENSIVE TEST SUITE")
    print("="*70)

    # Ensure test_results directory exists
    os.makedirs('test_results', exist_ok=True)

    tests = [
        ("pytest tests/test_unit.py -v", "UNIT TESTS"),
        ("pytest tests/test_integration.py -v", "INTEGRATION TESTS"),
        ("pytest tests/test_edge_cases.py -v", "EDGE CASES & STRESS TESTS"),
        ("pytest tests/test_data_integrity.py -v", "DATA INTEGRITY TESTS"),
        ("pytest tests/test_performance.py -v -s", "PERFORMANCE TESTS"),
    ]

    results = []
    for cmd, description in tests:
        returncode = run_command(cmd, description)
        results.append((description, returncode))

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)

    all_passed = True
    for description, returncode in results:
        status = "✓ PASSED" if returncode == 0 else "✗ FAILED"
        print(f"{description:40} {status}")
        if returncode != 0:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n✓ ALL TESTS PASSED! Your Excel Translator is ready.")
        print("  You can proceed with Supabase backend integration.")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED. Please review the errors above.")
        return 1


def run_with_coverage():
    """Run tests with coverage report"""
    print("\n" + "="*70)
    print("  RUNNING TESTS WITH COVERAGE")
    print("="*70)

    cmd = "pytest tests/ --cov=excel_translator --cov-report=html --cov-report=term"
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("\n✓ Coverage report generated: htmlcov/index.html")

    return result.returncode


def run_performance_only():
    """Run only performance benchmarks"""
    print("\n" + "="*70)
    print("  PERFORMANCE BENCHMARKS")
    print("="*70)

    cmd = "pytest tests/test_performance.py --benchmark-only -v"
    result = subprocess.run(cmd, shell=True)

    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coverage":
            sys.exit(run_with_coverage())
        elif sys.argv[1] == "--performance":
            sys.exit(run_performance_only())
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_tests.py              # Run all tests")
            print("  python run_tests.py --coverage   # Run with coverage report")
            print("  python run_tests.py --performance # Run performance benchmarks only")
            sys.exit(0)

    sys.exit(main())
