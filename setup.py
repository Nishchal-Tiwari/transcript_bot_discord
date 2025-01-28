from setuptools import setup, find_packages

setup(
    name="zerve",  # Name of your project
    version="0.1",
    packages=find_packages(where="src"),  # Specify the source directory
    package_dir={"": "src"},  # Map the source directory
    install_requires=[],  # Add your dependencies here
)
