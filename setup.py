from setuptools import find_packages, setup
import os

VERSION = "0.8"
DESCRIPTION = "A simple proxy finder"
INSTALL_REQUIRES = ["beautifulsoup4==4.13.3", "peewee==3.17.9", "requests==2.32.3"]
if os.name == "nt":
    INSTALL_REQUIRES.append("windows-curses==2.4.1")

setup(
    name="proxyfinder",
    version=VERSION,
    author="CalumRakk",
    author_email="leocasti2@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    keywords=["python", "proxy", "finder", "checker", "scraper"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "proxyfinder=proxyfinder.cli:main",
        ],
    },
)
