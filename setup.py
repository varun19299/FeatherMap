from setuptools import find_packages, setup

setup(
    name="feathermap",
    version="1.0",
    packages=find_packages(include=["feathermap"]),
    install_requires=[
        "torch",
        "torchvision",
        "packaging",
        "numpy",
        "pandas",
        "matplotlib",
    ],
)
