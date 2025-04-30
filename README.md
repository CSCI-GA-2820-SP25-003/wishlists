# Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SP25-003/wishlists/actions/workflows/workflow.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-003/wishlists/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/wishlists/graph/badge.svg?token=39H36Y8ODQ)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/wishlists)
This repository contains code for Wishlists for an e-commerce web site. Wishlists are comprised of Products. The services can be accessed through REST API routes.

## Models Overview

Wishlists have the following fields:

```text
- id
- name
- userid
- products
```

Wishlist Products have the following fields:

```text
- id
- wishlist_id
- name
- price
- description
```

## Contents

```text
.dockerignore               - exclude files from build context
.gitignore                  - this will ignore vagrant and other metadata files
.flaskenv                   - Environment variables to configure Flask
.gitattributes              - File to gix Windows CRLF issues
Dockerfile                  - instructions to generate Docker image
LICENSE                     - Apache license
Makefile                    - defines commands for building program
Pipfile                     - specifies top level requirements
Pipfile.lock                - specifies package versions
Procfile                    - commands executed on startup
docker-compose.yml          - enables multi-container applications
docker-compose.debug.yml    - enables debugger
.devcontainers/             - Folder with support for VSCode Remote Containers
dot-env-example             - copy to .env to use environment variables
requirements.txt            - required packages and libraries
setup.cfg                   - configuration file
wsgi.py                     - web server gateway interface entry point
.tekton/
features/
├── steps/
k8s/
├── postgres/
    ├── postgres-deployment.yaml
    ├── postgres-service.yaml
    ├── secret.yaml
├── deployment.yaml
├── ingress.yaml
├── service.yaml
service/                    - service python package
├── __init__.py             - package initializer
├── config.py               - configuration parameters
├── routes.py               - module with service routes
├── common                  - common code package
    ├── cli_commands.py     - Flask command to recreate all tables
    ├── error_handlers.py   - HTTP error handling code
    ├── log_handlers.py     - logging setup code
    └── status.py           - HTTP status constants
└── models                  - business models package
    ├── __init__.py         - package initializer
    ├── persistent_base.py  - module with Persistent Base model
    ├── product.py          - module with Product model
    └── wishlist.py         - module with Wishlist model

tests/                      - test cases package
├── __init__.py             - package initializer
├── factories.py            - Factory for testing with fake objects
├── test_cli_commands.py    - test suite for the CLI
├── test_product.py         - test suite for Products
├── test_wishlist.py        - test suite for Wishlists
└── test_routes.py          - test suite for service routes
```

## Information about this repo

```text
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

list_wishlists    GET      /wishlists
create_wishlists  POST     /wishlists
get_wishlists     GET      /wishlists/<wishlist_id>
update_wishlists  PUT      /wishlists/<wishlist_id>
delete_wishlists  DELETE   /wishlists/<wishlist_id>

list_products     GET      /wishlists/<int:wishlist_id>/products
create_products   POST     /wishlists/<wishlist_id>/products
get_products      GET      /wishlists/<wishlist_id>/products/<product_id>
update_products   PUT      /wishlists/<wishlist_id>/products/<product_id>
delete_products   DELETE   /wishlists/<wishlist_id>/products/<product_id>
```

## Running and Testing

Calling `make run` will run the service on localhost:8080.

The service can be tested using `make test`.

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
