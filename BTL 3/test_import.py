#!/usr/bin/env python3
"""Test import rag_query module"""

print("Đang import rag_query...")

try:
    import rag_query
    print("✓ rag_query imported successfully")
    print(f"  - retrieve: {type(rag_query.retrieve)}")
    print(f"  - generate: {type(rag_query.generate)}")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
