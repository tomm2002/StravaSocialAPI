import email
from setuptools import setup, find_packages

setup(
    name="StravaSocialAPI",
    version="0.0.2",
    author="Tomo",
    description="API for Strava that interacts with the social media",
    packages=['StravaSocialAPI'],
    install_requires=[
        "selenium",  
    ],
)

