#!/usr/bin/env python
"""
Simple script to run tests with the proper path setup.
"""
import sys
import os
import pytest

# Add the current directory to Python path to enable imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Run pytest
    sys.exit(pytest.main(['tests/test_registration.py'] + sys.argv[1:])) 