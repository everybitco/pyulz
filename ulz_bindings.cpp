#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "ulz.hpp"

namespace py = pybind11;

class PyULZ {
private:
    CULZ ulz;
    
public:
    PyULZ() {}
    
    py::bytes compress(const py::bytes &data, int level = 5) {
        if (level < 1 || level > 9) {
            throw std::runtime_error("Compression level must be between 1 and 9");
        }
        
        std::string data_str = data;
        const CULZ::U8* input = reinterpret_cast<const CULZ::U8*>(data_str.data());
        size_t input_size = data_str.size();
        
        if (input_size > static_cast<size_t>(std::numeric_limits<int>::max() - CULZ::EXCESS)) {
            throw std::runtime_error("Input data too large (max ~2GB)");
        }
        
        // Allocate output buffer using the same formula as original code
        size_t output_buffer_size = input_size + CULZ::EXCESS;
        std::vector<CULZ::U8> output(output_buffer_size);
        
        int compressed_size = ulz.Compress(
            const_cast<CULZ::U8*>(input), 
            static_cast<int>(input_size),
            output.data(), 
            level
        );
        
        if (compressed_size < 0) {
            throw std::runtime_error("Compression failed");
        }
        
        if (compressed_size > static_cast<int>(output_buffer_size)) {
            throw std::runtime_error("Compressed data exceeds buffer size");
        }
        
        return py::bytes(reinterpret_cast<const char*>(output.data()), compressed_size);
    }
    
    py::bytes decompress(const py::bytes &compressed_data, size_t original_size = 0) {
        std::string data_str = compressed_data;
        const CULZ::U8* input = reinterpret_cast<const CULZ::U8*>(data_str.data());
        size_t input_size = data_str.size();
        
        if (input_size > static_cast<size_t>(std::numeric_limits<int>::max())) {
            throw std::runtime_error("Input data too large (max 2GB)");
        }

        // If original_size not provided, estimate it
        size_t estimated_output_size;
        if (original_size > 0) {
            estimated_output_size = original_size;
        } else {
            // Use a reasonable heuristic: compressed data can expand up to ~4x
            estimated_output_size = input_size * 4;
        }
        
        // Check output size limit
        if (estimated_output_size > static_cast<size_t>(std::numeric_limits<int>::max() - CULZ::EXCESS)) {
             throw std::runtime_error("Estimated output size too large (max ~2GB)");
        }
        
        // Allocate output buffer with extra space
        size_t output_buffer_size = estimated_output_size + CULZ::EXCESS;
        std::vector<CULZ::U8> output(output_buffer_size);
        
        // Decompress
        int decompressed_size = ulz.Decompress(
            const_cast<CULZ::U8*>(input),
            static_cast<int>(input_size),
            output.data(),
            static_cast<int>(estimated_output_size)
        );
        
        if (decompressed_size < 0) {
            throw std::runtime_error("Decompression failed");
        }
        
        if (decompressed_size > static_cast<int>(estimated_output_size)) {
            throw std::runtime_error("Decompressed data exceeds estimated size");
        }
        
        // Convert back to Python bytes
        return py::bytes(reinterpret_cast<const char*>(output.data()), decompressed_size);
    }
    
    // Alternative method that handles unknown output sizes
    std::pair<py::bytes, size_t> decompress_with_size(const py::bytes &compressed_data) {
        std::string data_str = compressed_data;
        const CULZ::U8* input = reinterpret_cast<const CULZ::U8*>(data_str.data());
        size_t input_size = data_str.size();
        
        if (input_size > static_cast<size_t>(std::numeric_limits<int>::max())) {
            throw std::runtime_error("Input data too large (max 2GB)");
        }

        // Start with a reasonable buffer size and grow if needed
        size_t estimated_output_size = input_size * 4;
        std::vector<CULZ::U8> output;
        int decompressed_size;
        
        // Try with increasing buffer sizes until successful
        while (true) {
            // Check limit before resizing
            if (estimated_output_size > static_cast<size_t>(std::numeric_limits<int>::max() - CULZ::EXCESS)) {
                 // Cap at max allowed
                 estimated_output_size = static_cast<size_t>(std::numeric_limits<int>::max() - CULZ::EXCESS);
            }

            output.resize(estimated_output_size + CULZ::EXCESS);
            
            decompressed_size = ulz.Decompress(
                const_cast<CULZ::U8*>(input),
                static_cast<int>(input_size),
                output.data(),
                static_cast<int>(estimated_output_size)
            );
            
            if (decompressed_size >= 0) {
                break;
            }
            
            // If we are already at max, fail
            if (estimated_output_size >= static_cast<size_t>(std::numeric_limits<int>::max() - CULZ::EXCESS)) {
                throw std::runtime_error("Decompression failed: output size too large or data corrupt");
            }

            // Buffer too small, try larger
            estimated_output_size *= 2;
        }
        
        py::bytes result = py::bytes(reinterpret_cast<const char*>(output.data()), decompressed_size);
        return {result, static_cast<size_t>(decompressed_size)};
    }
};

PYBIND11_MODULE(pyulz, m) {
    m.doc() = "Python bindings for ULZ - fast LZ77 compression library";
    
    py::class_<PyULZ>(m, "ULZ")
        .def(py::init<>())
        .def("compress", &PyULZ::compress, 
             py::arg("data"), 
             py::arg("level") = 5,
             "Compress data using ULZ algorithm. Level 1-9 (default: 5)")
        .def("decompress", &PyULZ::decompress, 
             py::arg("compressed_data"), 
             py::arg("original_size") = 0,
             "Decompress ULZ compressed data. Optionally specify original size for efficiency")
        .def("decompress_with_size", &PyULZ::decompress_with_size, 
             py::arg("compressed_data"),
             "Decompress ULZ compressed data and return (data, size) tuple");
    
    m.attr("__version__") = "1.0.0";
    
    m.attr("WINDOW_SIZE") = CULZ::WINDOW_SIZE;
    m.attr("MIN_MATCH") = CULZ::MIN_MATCH;
    m.attr("EXCESS") = CULZ::EXCESS;
}