"""Setup script for Contact Importer."""

import os
from pathlib import Path
from setuptools import setup, find_packages

# Read version from a version file or set it here
__version__ = "1.0.0"

# Get the long description from README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Telegram Contact Importer - Bulk import phone numbers to your Telegram account"

# Parse requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() 
            for line in fh 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "click>=8.0.0",
        "phonenumbers>=8.13.0",
        "pandas>=1.5.0",
        "tqdm>=4.64.0",
        "colorama>=0.4.4",
        "telethon>=1.30.0",
        "cryptg>=0.4.0",
        "openpyxl>=3.1.0",
        "vobject>=0.9.6",
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.990",
    "pytest-asyncio>=0.20.0",
    "pytest-cov>=4.0.0",
]

setup(
    name="telegram-contact-importer",
    version=__version__,
    author="Gibson Kamau (Domains18)",
    author_email="",  # Add email if available
    description="A CLI tool to bulk import phone numbers to Telegram contacts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Domains18/ct226",
    project_urls={
        "Bug Reports": "https://github.com/Domains18/ct226/issues",
        "Source": "https://github.com/Domains18/ct226",
        "Documentation": "https://github.com/Domains18/ct226/blob/main/README.md",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    keywords="telegram, contacts, import, cli, phone-numbers, bulk-import",
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "telegram-contact-importer=main:main",
            "tci=main:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.yaml", "*.txt"],
        "src": ["data/*.txt"],
    },
    zip_safe=False,
    platforms=["any"],
)
