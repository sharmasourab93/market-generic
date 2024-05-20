from setuptools import find_packages, setup

NAME = "market-generic"
__version__ = "0.0.1"
DESCRITPION = "A Generic Python Package for Stock Market Analysis and Trading"
URL = "https://github.com/sharmasourab93/market-generic"
AUTHOR = "Sourab S Sharma"
EMAIL = "sharmasourab93@gmail.com"

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt", "r") as file:
    INSTALL_REQUIRES = [line.strip() for line in file.readlines()]

KEYWORDS = ["Market", "Trade", "Analysis"]

setup(
    name=NAME,
    version=__version__,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRITPION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=["tests", ".github"]),
    setup_requires=["wheel"],
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
)
