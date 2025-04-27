from setuptools import setup, find_packages

setup(
    name="gptchat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "gptchat = gptchat.main:main",
        ],
    },
)
