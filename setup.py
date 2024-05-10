from setuptools import find_packages, setup

NAME = "generic-trade"
VERSION = "0.0"
DESCRITPION = "A Generic Python Package for Stock Market Analysis and Trading"
URL = "https://github.com/sharmasourab93/Trade"
AUTHOR = "Sourab S Sharma"
EMAIL = "sharmasourab93@gmail.com"

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt", "r") as file:
    INSTALL_REQUIRES = [line.strip() for line in file.readlines()]

KEYWORDS = ["Market", "Trade", "Analysis"]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRITPION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=["tests"]),
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
)
