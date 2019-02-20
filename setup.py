#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    # "luci==1.0.0b1",
    "colorama==0.4.1",
    "termcolor==1.1.0",
    "terminaltables==3.1.0",
    "Pygments==2.3.1",
    "passlib==1.7.1",
    "treelib==1.5.3"
    # "templig==1.0.0b1"
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
        # "console_scripts": [
        # "freckles=freckles.freckles_cli:cli",
        # "frecklecute=freckles.frecklecute_cli:cli",
        # "frecklet=freckles.frecklet_cli:cli",
        # "freckfreckfreck=freckles.freckfreckfreck.freckfreckfreck_cli:cli",
        # "fff=freckles.freckfreckfreck.freckfreckfreck_cli:cli",
        # "freckelize=freckles.freckelize.freckelize_cli:cli",
        # ],
        # "luci.index_item_types": ["frecklet=freckles.frecklet:Frecklet"],
        # "freckles.adapters": [
        #     "freckles=freckles.adapters.freckles_adapter:FrecklesChildAdapter"
        # ],
        # "freckfreckfreck.plugins": [
        #     "config=freckles.freckfreckfreck.fff_cnf_plugin:cnf",
        #     "frecklet=freckles.freckfreckfreck.fff_frecklet_plugin:frecklet",
        #     "doc=freckles.freckfreckfreck.fff_doc_plugin:doc",
        #     "frecklets=freckles.freckfreckfreck.fff_frecklet_plugin:frecklets",
        #     "repos=freckles.freckfreckfreck.fff_repos_plugin:repos",
        #     "utils=freckles.freckfreckfreck.fff_utils_plugin:utils",
        #     "filter=freckles.freckfreckfreck.fff_filter_plugin:filter",
        # ],
        "freckelize.plugins": [
            "init=freckles.freckelize.freckelize_init_plugin:init_freckle",
            "update=freckles.freckelize.freckelize_init_plugin:update_freckle",
        ],
        "freckles.callbacks": [
            "freckles=freckles.output_callback:DefaultCallback",
            "dummy=freckles.output_callback:DummyCallback",
            "simple=freckles.output_callback:SimpleCallback"
            # "spinner=freckles.callbacks:SpinnerCallback"
        ],
    },
    install_requires=requirements,
    license="Parity Public License 5.0.0",
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
