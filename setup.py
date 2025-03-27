from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION = "Un simple buscador de proxies"

setup(
    name="proxyfinder",
    version=VERSION,
    author="CalumRakk",
    author_email="leocasti2@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.13.3",
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "idna==3.10",
        "requests==2.32.3",
        "soupsieve==2.6",
        "typing_extensions==4.13.0",
        "urllib3==2.3.0",
    ],
    keywords=["python", "proxy", "finder", "checker", "scraper"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "proxyfinder=proxyfinder.script:main",
        ],
    },
)
