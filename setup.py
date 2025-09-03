from setuptools import setup, find_packages

setup(
    name="essalud-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pandas==2.2.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "gdown==4.7.1",
        "requests==2.31.0",
        "numpy==1.24.3",
    ],
    python_requires=">=3.11",
)
