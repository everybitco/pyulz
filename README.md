**PyULZ** is a high-performance Python extension that provides bindings for the **ULZ (Ultra-fast LZ77)** compression library.

## What It Does

PyULZ allows you to compress and decompress binary data (bytes) directly in Python with extremely low latency.

**The Algorithm**: ULZ is a derivative of the **LZ77** algorithm. It works by finding repeated patterns in the data (a "sliding window") and replacing them with references (distance and length pairs) to previous occurrences.

*   It uses a hash chain to quickly find matches.
*   It prioritizes speed over maximum compression ratio, making it significantly faster than standard Deflate (zlib) or Gzip, though the output file size might be slightly larger.

I will do a through research on potential use cases for PyULZ and update this README with more information.

Look at examples folder for more usage examples. 

## Installation

```bash
pip install .
```

## Usage

```python
import pyulz

ulz = pyulz.ULZ()

# Compress
data = b"Repeated data " * 1000
compressed = ulz.compress(data, level=1) # Level 1 (fastest) to 9 (best)

# Decompress
original = ulz.decompress(compressed)
```

## Limitations

*   **2GB File Size Limit**: The underlying C++ library uses 32-bit signed integers for indexing. Consequently, PyULZ cannot process single data chunks larger than **2GB**. For larger files, you must split the data into smaller blocks.
