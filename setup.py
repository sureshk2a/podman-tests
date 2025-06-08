from setuptools import setup, find_packages

setup(
    name="podman-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "acp-sdk",
        "httpx>=0.24.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0"
    ],
) 