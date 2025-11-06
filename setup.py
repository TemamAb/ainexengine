from setuptools import setup, find_packages

setup(
    name="ainexus",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "gunicorn==21.2.0", 
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "aiohttp==3.9.1",
        "ccxt==4.1.72",
        "numpy==1.24.3",
    ],
    python_requires=">=3.8",
)
