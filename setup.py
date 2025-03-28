from setuptools import find_packages, setup

VERSION = "0.5"
DESCRIPTION = "Un simple buscador de proxies"

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
            "proxyfinder=proxyfinder.script:main",
        ],
    },
)
