# pvmon

![Python package](https://github.com/alexclaydon/pvmon/workflows/Python%20package/badge.svg)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Designed to assist with simplifying and automating the monitoring of solar photovoltaic installations making use of NTT's ecomegane subscription service delivered over LTE.  Written in a combination of object-oriented and functional styles.  

Originally developed to meet a specific business need.  No affiliation with NTT generally or the ecomegane service in particular.

## Configuration

* Currently only designed to work with Firefox as the Selenium back-end.  You'll need to have Firefox installed and the gecko webdriver (https://github.com/mozilla/geckodriver/releases) in your path.
* You will need to create 'service-cfg.yml' in the working directory from 'templates/config.yml', inserting your own user details.
* The codebase uses a custom logging library which is not public at this time - you will need to fork and setup your own logger, or else download without cloning and modify accordingly.

## Notes

* This version of the codebase was developed as an object-oriented wrapper over a set of discrete functions originally developed on an ad-hoc basis as the problem domain was explored.  Future refactoring will focus first on codebase consistency before adding new features.
* Git history prior to making this repo public has been deleted to prevent the unintentional disclosure of any commercially sensitive information.
* TODOs remain in the code.
