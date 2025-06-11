#!/usr/bin/env python3
"""
Setup script for AID Commander
Makes AID Commander pip-installable
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="aid-commander",
    version="2.0.0",
    author="AID Development Team",
    author_email="aid@sistronics.com",
    description="AI-Facilitated Iterative Development - Terminal Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sistronics/aid-commander",
    packages=find_packages(),
    py_modules=[
        'aid_commander',
        'template_engine', 
        'ai_service',
        'logger',
        'ai_setup_wizard'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (none required for basic functionality)
    ],
    extras_require={
        "ai": [
            "aiohttp>=3.8.0",  # For AI provider communication
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "all": [
            "aiohttp>=3.8.0",
            "pytest>=6.0", 
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aid-commander=aid_commander:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords=[
        "ai", "development", "project-management", "cli", "automation", 
        "templates", "task-management", "iterative-development"
    ],
    project_urls={
        "Bug Reports": "https://github.com/sistronics/aid-commander/issues",
        "Source": "https://github.com/sistronics/aid-commander",
        "Documentation": "https://github.com/sistronics/aid-commander/blob/main/USER_GUIDE.md",
    },
)