#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all files have proper encoding
"""
import os
import sys

def test_file_encoding(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return True
    except UnicodeDecodeError as e:
        print(f"Encoding error in {filepath}: {e}")
        return False

def test_all_python_files():
    print("Testing Python file encoding...")
    all_good = True
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if not test_file_encoding(filepath):
                    all_good = False
    
    if all_good:
        print("✅ All Python files have proper UTF-8 encoding")
    else:
        print("❌ Some files have encoding issues")
    
    return all_good

if __name__ == "__main__":
    success = test_all_python_files()
    sys.exit(0 if success else 1)
