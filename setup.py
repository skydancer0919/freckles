#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import io

from setuptools import setup, find_packages

with io.open("README.rst", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with io.open("HISTORY.rst", encoding="utf-8") as history_file:
    history = history_file.read()

requirements = [
    "frkl==1.0.0b1",
    "frkl-pkg==0.1.0",
    "ting==1.0.0b1",
    "termcolor==1.1.0",
    "tabulate==0.8.3",
    "Pygments==2.3.1",
    "passlib==1.7.1",
    # "templig==1.0.0b1"
    "pymdown-extensions==6.0",
    "exodus-bundler==2.0.2",
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Markus Binsteiner",
    author_email="makkus@frkl.io",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Elastic scripting",
    entry_points={
        "freckelize.plugins": [
            "init=freckles.freckelize.freckelize_init_plugin:init_freckle",
            "update=freckles.freckelize.freckelize_init_plugin:update_freckle",
        ],
        "frutil_tasks.callbacks": [
            "freckles=freckles.output_callback:DefaultCallback",
            # "spinner=freckles.callbacks:SpinnerCallback"
        ],
        "freckles.adapters": [
            "shell=freckles.adapters.shell.freckles_adapter_shell:FrecklesAdapterShell"
        ],
    },
    install_requires=requirements,
    license="Parity Public License 6.0.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="freckles",
    name="freckles",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.com/makkus/freckles",
    version="1.0.0b1",
    zip_safe=False,
)
