import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vttmisc",
    version="0.0.5",
    author="Aaron Bell",
    author_email="hello@sajatypeworks.com",
    description="A collection of misc scripts related to VTT",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaronbell/vttmisc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires="fontTools>=4.15.0",
    python_requires='>=3.6',
)