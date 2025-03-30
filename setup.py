from setuptools import find_packages, setup
import os

VERSION = "0.5"
DESCRIPTION = "A simple proxy finder"
WINDOWS_DEPENDENCIES = ["windows-curses==2.4.1"] if os.name == "nt" else []

setup(
    name="proxyfinder",
    version=VERSION,
    author="CalumRakk",
    author_email="leocasti2@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=["beautifulsoup4==4.13.3", "peewee==3.17.9", "requests==2.32.3"],
    keywords=["python", "proxy", "finder", "checker", "scraper"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "proxyfinder=proxyfinder.cli:main",
        ],
    },
    extras_require={
        "win": WINDOWS_DEPENDENCIES,
    },
)
