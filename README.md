# Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This repository contains code for Wishlists for an e-commerce web site. Wishlists are comprised of Products. The services can be accessed through REST API routes.

## Models Overview
Wishlists have the following fields:
```
- id
- name
- userid
- products
```
Wishlist Products have the following fields:
```
- id
- wishlist_id
- name
- price
- description
```

## Information about this repo
```
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
