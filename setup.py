from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.md", "r").read()

setup(
    name="pareto-liquidator",
    version="0.1.0",
    author="grubiroth",
    author_email="mike@paretolabs.xyz",
    packages=find_packages(),
    description="Bot for maintaining Pareto's oracles",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/pareto-xyz/pareto-liquidation-bot-v1",
    install_requires=[
        "requests==2.28.1",
        "setuptools==41.2.0",
        "web3==5.30.0",
    ]
)
