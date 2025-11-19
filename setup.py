from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import platform

class get_pybind_include:
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked."""
    
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)

if platform.system() == "Windows":
    extra_compile_args = ['/O2', '/std:c++11']
else:
    extra_compile_args = ['-O3', '-std=c++11']

ext_modules = [
    Extension(
        'pyulz',
        sources=[
            'ulz_bindings.cpp',
        ],
        include_dirs=[
            get_pybind_include(),
            get_pybind_include(user=True),
            '.'  # Include the current directory for ulz.hpp
        ],
        language='c++',
        extra_compile_args=extra_compile_args,
    ),
]

# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler."""
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True

class BuildExt(build_ext):
    c_opts = {
        'msvc': ['/EHsc', '/O2'],
        'unix': ['-O3', '-std=c++11'],
    }
    
    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']
    
    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

setup(
    name='pyulz',
    version='1.0.0',
    author='ULZ Python Bindings',
    author_email='vinayak@everybit.co',
    description='Python bindings for ULZ - fast LZ77 compression library',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/everybitco/pyulz',
    ext_modules=ext_modules,
    install_requires=[
        'pybind11>=2.10.0',
    ],
    setup_requires=[
        'pybind11>=2.10.0',
    ],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Compression',
        'License :: OSI Approved :: Public Domain',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: C++',
    ],
)