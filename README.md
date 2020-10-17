# pvmon

![Docker Image CI](https://github.com/alexclaydon/pvmon/workflows/Docker%20Image%20CI/badge.svg)

![Python package](https://github.com/alexclaydon/pvmon/workflows/Python%20package/badge.svg)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Designed to assist with simplifying and automating the monitoring of solar photovoltaic installations making use of NTT's ecomegane subscription service delivered over LTE.  Written in an imperative shell, functional core style.  

Originally developed to meet a specific business need.  No affiliation with NTT generally or the ecomegane service in particular.

## Configuration

* Currently only designed to work with Firefox as the Selenium back-end.  You'll need to have Firefox installed and the [gecko webdriver](https://github.com/mozilla/geckodriver/releases) in your path.  If you deploy with Docker, the included Dockerfile takes care of this.
* The execution environment requires that `PUSHOVER_USER` and `PUSHOVER_TOKEN` environment variables be available to enable [Pushover](https://pushover.net/) notifications on iOS.  If you deploy with Docker, these can be included in a `.env` file in the root directory, where Docker will look for them automatically and pass them to the container runtime.
* You will also need to create a `service-cfg.yml` in the `resources` directory (based on the template available at `resources/templates/service-cfg.yml`, inserting your own user login information for ecomegane.  If you deploy with Docker, you can either map that directory to a volume on the host, or `ssh` into the running container and create it.  In future, service configuration will be handled with environment variables instead.

## Notes

* This version of the codebase was developed as an object-oriented wrapper over a set of discrete functions originally developed on an ad-hoc basis as the problem domain was explored.
* Git history prior to making this repo public has been deleted to prevent the unintentional disclosure of any commercially sensitive information.
* TODOs remain in the code.
