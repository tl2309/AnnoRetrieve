#!/usr/bin/env python3
"""
Simple test script for AnnoRetrieve system (without heavy model loading)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DATA_PATHS, SCHEMA_CONFIG
from fp_growth_impl import find_frequent_itemsets


def test_fp_growth():
    """测试FP-Growth算法实现"""
    print("Testing FP-Growth Implementation...")
    
    # 测试数据
    test_transactions = [
        ['milk', 'bread', 'eggs'],
        ['milk', 'bread', 'butter'],
        ['milk', 'cheese'],
        ['bread', 'butter'],
        ['milk', 'bread', 'eggs', 'butter'],
        ['milk', 'bread', 'eggs', 'cheese'],
        ['bread', 'eggs'],
        ['milk', 'eggs'],
        ['milk', 'bread', 'eggs', 'butter', 'cheese'],
        ['cheese', 'butter']
    ]
    
    # 查找频繁项集
    min_support = 3
    frequent_itemsets = find_frequent_itemsets(test_transactions, min_support)
    
    print(f"  Minimum support: {min_support}")
    print(f"  Found {len(frequent_itemsets)} frequent itemsets")
    print(f"  Frequent itemsets: {frequent_itemsets}")
    
    return len(frequent_itemsets) > 0


def test_config():
    """测试配置加载"""
    print("\nTesting Configuration...")
    
    print(f"  Schema versions: {list(SCHEMA_CONFIG['schema_versions'].keys())}")
    print(f"  Layers: {list(SCHEMA_CONFIG['layers'].keys())}")
    print(f"  Quality weights: {SCHEMA_CONFIG['quality_weights']}")
    print(f"  Constraints: {SCHEMA_CONFIG['constraints']}")
    
    return True


def test_data_paths():
    """测试数据路径配置"""
    print("\nTesting Data Paths...")
    
    print(f"  Datalake path: {DATA_PATHS['datalake']}")
    print(f"  Candidate path: {DATA_PATHS['candidate']}")
    print(f"  Annotations path: {DATA_PATHS['annotations']}")
    print(f"  Schemas path: {DATA_PATHS['schemas']}")
    
    # 检查路径是否存在
    datalake_exists = os.path.exists(DATA_PATHS['datalake'])
    print(f"  Datalake path exists: {datalake_exists}")
    
    return datalake_exists


def main():
    """主测试函数"""
    print("=== Simple AnnoRetrieve System Test ===")
    
    tests = [
        ("FP-Growth Algorithm", test_fp_growth),
        ("Configuration", test_config),
        ("Data Paths", test_data_paths)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name}: PASSED")
                passed_tests += 1
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
    
    print(f"\n=== Test Results: {passed_tests}/{total_tests} tests passed ===")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The core functionality of AnnoRetrieve is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
