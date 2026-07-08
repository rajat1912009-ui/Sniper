from setuptools import setup, find_packages

setup(
    name="track-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "mutagen",
        "requests",
        "Pillow"
    ],
    entry_points={
        "console_scripts": [
            "Sniper=track_cli.Sniper:main",  # Creates a permanent terminal keyword
        ],
    },
)
