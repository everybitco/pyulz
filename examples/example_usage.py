## Usage: python example_usage.py <file_to_compress>

import sys
import os
import time
import pyulz

import hashlib

def get_hash(data):
    return hashlib.sha256(data).hexdigest()

def main():
    print(f"PyULZ Version: {pyulz.__version__}")
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = os.path.join(os.path.dirname(__file__), 'wordle.txt')
    
    if not os.path.exists(input_file):
        print(f"Usage: python example_usage.py <file_to_compress>")
        print(f"Error: Default file '{input_file}' not found.")
        return

    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    original_size = len(data)
    print(f"Original size: {original_size} bytes ({original_size / 1024 / 1024:.2f} MB)")
    
    if original_size == 0:
        print("Warning: Input file is empty.")
    
    # Sanity Check: 2GB Limit
    if original_size > 2 * 1024 * 1024 * 1024 - 1024: # ~2GB safety margin
        print("Error: Input file exceeds the 2GB limit of the ULZ library.")
        return

    # Calculate hash of original data
    print("Calculating SHA256 hash of original data...")
    original_hash = get_hash(data)
    print(f"Original Hash: {original_hash}")
    
    ulz = pyulz.ULZ()
    
    # Test Compression
    print("\n--- Compression Test ---")
    try:
        start_time = time.time()
        compressed = ulz.compress(data, level=9)
        end_time = time.time()
        
        compressed_size = len(compressed)
        ratio = (compressed_size / original_size) * 100 if original_size > 0 else 0
        print(f"Compressed size: {compressed_size} bytes ({compressed_size / 1024 / 1024:.2f} MB)")
        print(f"Compression Ratio: {ratio:.2f}%")
        print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
    except RuntimeError as e:
        print(f"Compression Failed: {e}")
        return

    # Test Decompression (known size)
    print("\n--- Decompression Test (Known Size) ---")
    try:
        start_time = time.time()
        decompressed = ulz.decompress(compressed, original_size=original_size)
        end_time = time.time()
        
        print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
        
        # Verify
        if len(decompressed) != original_size:
             print(f"FAILURE: Decompressed size mismatch! Expected {original_size}, got {len(decompressed)}")
        elif get_hash(decompressed) == original_hash:
            print("SUCCESS: Decompressed data matches original (Hash Verified).")
        else:
            print("FAILURE: Decompressed data hash does NOT match original!")
            
        del decompressed
        
    except RuntimeError as e:
        print(f"Decompression Failed: {e}")

    # Test Decompression (unknown size)
    print("\n--- Decompression Test (Unknown Size) ---")
    try:
        start_time = time.time()
        decompressed_auto, size = ulz.decompress_with_size(compressed)
        end_time = time.time()
        
        print(f"Decompressed size detected: {size}")
        print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
        
        if size != original_size:
             print(f"FAILURE: Detected size mismatch! Expected {original_size}, got {size}")
        elif get_hash(decompressed_auto) == original_hash:
            print("SUCCESS: Decompressed data matches original (Hash Verified).")
        else:
            print("FAILURE: Decompressed data hash does NOT match original!")
            
    except RuntimeError as e:
        print(f"Decompression (Unknown Size) Failed: {e}")

if __name__ == "__main__":
    main()
