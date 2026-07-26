from setuptools import setup, find_packages

setup(
    name="aqualabs",
    version="4.0.0",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.0",
        "matplotlib>=3.7.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aqualabs=aqualabs.app:main",
        ],
    },
    author="AquaLabs",
    description="Water Treatment Lab Analysis Suite",
)
