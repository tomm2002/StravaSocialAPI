import email
from setuptools import setup, find_packages

setup(
    name="StravaSocialAPI",
    version="0.0.4",
    author="Tomo",
    description="API for Strava that interacts with the social media",
    long_description = "API for Strava, focusing on social media. It is using Selenium web-scraper. Use it to follow, unfollow, give kudos, comment, get a kudos list, download GPX files, and more. Find more on gitbuh: https://github.com/tomm2002/StravaSocialAPI/tree/master",
    url="https://github.com/tomm2002/StravaSocialAPI/tree/master",
    packages=['StravaSocialAPI'],
    install_requires=[
        "selenium",  
    ],
)

