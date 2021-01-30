"""
Setup
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyNSL",
    version="0.0.1",
    author="Mikolaj Kegler",
    author_email="mikolajkegler@gmail.com",
    description="Python port of NSL package",
    long_description=long_description,
    url="https://github.com/MKegler/PyNSL",
    packages=setuptools.find_packages(),
    data_files=[('pyNSL', ['pyNSL/aud24.mat'])],
    python_requires='>=3.6',
)
