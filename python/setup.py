from setuptools import setup, find_packages

setup(
    name="volt-client",
    version="0.1.0",
    description="Python client for the Volt key-value database",
    author="Volt Team",
    py_modules=["volt_client"],
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
) 