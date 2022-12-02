# -*- coding: utf-8 -*-

import setuptools
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isCooking",
    python_requires='>=3.7',
    version="0.0.1",
    author="Jan Mrázek",
    author_email="email@honzamrazek.cz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaqwsx/isCooking",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pygsheets==2.0.5",
        "click>=7.1",
    ],
    zip_safe=False,
    include_package_data=True,
    entry_points = {
        "console_scripts": [
            "iscooking=iscooking.ui:cli",
        ],
    }
)
