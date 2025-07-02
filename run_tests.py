# run_tests.py - Main Test Runner
import subprocess
import sys
import os
from datetime import datetime

def run_test_group(group_number: int, description: str):
    """Run a specific test group"""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING GROUP {group_number}: {description}")
    print(f"{'='*60}")
    
    test_file = f"test_group_{group_number}_*.py"
    
    # Run pytest with verbose output and HTML report
    cmd = [
        "python", "-m", "pytest", 
        test_file,
        "-v",           # Verbose output
        "-s",           # Don't capture output
        "--tb=short"    # Short traceback format
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_all_tests():
    """Run all test groups sequentially"""
    print("🧪 API TESTING FRAMEWORK - FOUNDATION LEVEL")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Test groups to run
    test_groups = [
        (1, "Basic CRUD Operations"),
        (2, "Authentication & Security"),
        (3, "Data Relationships & Filtering"),
        (4, "Error Handling & Edge Cases"),
        (5, "Performance & Advanced Features")
    ]
    
    results = {}
    
    for group_num, description in test_groups:
        success = run_test_group(group_num, description)
        results[group_num] = success
        
        if success:
            print(f"✅ GROUP {group_num} PASSED")
        else:
            print(f"❌ GROUP {group_num} FAILED")
    
    # Summary report
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for group_num, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        description = dict(test_groups)[group_num]
        print(f"Group {group_num}: {description} - {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} groups passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Framework is ready for portfolio!")
    else:
        print("⚠️ Some tests failed. Check individual reports for details.")
    
    print(f"\n📋 Reports generated in 'reports/' directory")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def run_single_group():
    """Run a single test group (interactive)"""
    print("Available test groups:")
    print("1. Basic CRUD Operations")
    print("2. Authentication & Security")
    print("3. Data Relationships & Filtering")
    print("4. Error Handling & Edge Cases")
    print("5. Performance & Advanced Features")
    
    try:
        choice = int(input("\nEnter group number (1-5): "))
        if 1 <= choice <= 5:
            descriptions = {
                1: "Basic CRUD Operations",
                2: "Authentication & Security", 
                3: "Data Relationships & Filtering",
                4: "Error Handling & Edge Cases",
                5: "Performance & Advanced Features"
            }
            run_test_group(choice, descriptions[choice])
        else:
            print("Invalid choice. Please enter 1-5.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    print("🧪 API Testing Framework Runner")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all_tests()
        elif sys.argv[1].isdigit():
            group_num = int(sys.argv[1])
            if 1 <= group_num <= 5:
                descriptions = {
                    1: "Basic CRUD Operations",
                    2: "Authentication & Security", 
                    3: "Data Relationships & Filtering",
                    4: "Error Handling & Edge Cases",
                    5: "Performance & Advanced Features"
                }
                run_test_group(group_num, descriptions[group_num])
            else:
                print("Invalid group number. Use 1-5.")
        else:
            print("Usage: python run_tests.py [all|1|2|3|4|5]")
    else:
        print("Choose an option:")
        print("1. Run all test groups")
        print("2. Run single test group")
        
        choice = input("\nEnter choice (1 or 2): ")
        if choice == "1":
            run_all_tests()
        elif choice == "2":
            run_single_group()
        else:
            print("Invalid choice.")