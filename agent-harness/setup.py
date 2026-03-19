from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-openmaic",
    version="0.1.0",
    description="CLI-Anything harness for OpenMAIC",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.1.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-openmaic=cli_anything.openmaic.openmaic_cli:main",
        ],
    },
    python_requires=">=3.10",
)
