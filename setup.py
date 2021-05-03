from setuptools import setup, find_packages

setup(
    name="pylogger",
    packages=find_packages(exclude=["tests", "docs"]),
    version="1.0.0",
    description="Custom Python Logger for internal usage",
    author="Hariharan Ragothaman",
    classifiers=[
        "Topic:: Utilities",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
)
