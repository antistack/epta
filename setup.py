import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epta",
    version="0.0.1",
    author="antistack",
    author_email="",
    description="Utils for CV bots creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antistack/epta",
    project_urls={
        "Bug Tracker": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where=""),
    python_requires=">=3.9",
)
