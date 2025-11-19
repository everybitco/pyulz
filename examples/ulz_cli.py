## Usage: ulz_cli.py <command> <input_file> [-o <output_file>]
# <command> can be either 'pack' or 'unpack'
# <input_file> is the file to compress or decompress (can take .ulz)
# [-o <output_file>] is optional and specifies the output file name

import argparse
import os
import time
import pyulz
import sys

def compress_file(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found")
        return

    if output_path is None:
        output_path = input_path + ".ulz"

    print(f"Compressing '{input_path}' -> '{output_path}'...")
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        original_size = len(data)
        if original_size == 0:
            print("Warning: Input file is empty.")
        
        start = time.time()
        ulz = pyulz.ULZ()
        compressed = ulz.compress(data, level=9)
        end = time.time()
        
        with open(output_path, 'wb') as f:
            f.write(compressed)
            
        compressed_size = len(compressed)
        ratio = (compressed_size / original_size * 100) if original_size > 0 else 0
        
        print(f"Success! Saved to '{output_path}'")
        print(f"Original Size:   {original_size:,} bytes")
        print(f"Compressed Size: {compressed_size:,} bytes")
        print(f"Compression Ratio: {ratio:.2f}%")
        print(f"Time Taken: {(end-start)*1000:.2f} ms")
        
    except Exception as e:
        print(f"An error occurred during compression: {e}")

def decompress_file(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found")
        return

    if output_path is None:
        if input_path.endswith('.ulz'):
            output_path = input_path[:-4] # Remove .ulz
            # If the file already exists, append .restored to avoid accidental overwrite
            if os.path.exists(output_path):
                base, ext = os.path.splitext(output_path)
                output_path = f"{base}_restored{ext}"
        else:
            output_path = input_path + ".restored"

    print(f"Decompressing '{input_path}' -> '{output_path}'...")
    
    try:
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
            
        start = time.time()
        ulz = pyulz.ULZ()
        # We use decompress_with_size because we might not know the original size
        # when reading from a standalone file.
        decompressed, size = ulz.decompress_with_size(compressed_data)
        end = time.time()
        
        with open(output_path, 'wb') as f:
            f.write(decompressed)
            
        print(f"Success! Saved to '{output_path}'")
        print(f"Decompressed Size: {size:,} bytes")
        print(f"Time Taken: {(end-start)*1000:.2f} ms")
        
    except Exception as e:
        print(f"An error occurred during decompression: {e}")

def main():
    parser = argparse.ArgumentParser(description="PyULZ File Compressor/Decompressor Tool")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to run')
    
    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Compress a file')
    pack_parser.add_argument('file', help='Path to the file to compress')
    pack_parser.add_argument('-o', '--output', help='Optional output filename')
    
    # Unpack command
    unpack_parser = subparsers.add_parser('unpack', help='Decompress a .ulz file')
    unpack_parser.add_argument('file', help='Path to the .ulz file to decompress')
    unpack_parser.add_argument('-o', '--output', help='Optional output filename')
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.command == 'pack':
        compress_file(args.file, args.output)
    elif args.command == 'unpack':
        decompress_file(args.file, args.output)

if __name__ == "__main__":
    main()
