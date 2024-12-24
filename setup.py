from setuptools import setup, find_packages

setup(
    name="crypto_monitor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'pandas',
        'numpy',
        'pytest',
        'python-dotenv',
    ],
)