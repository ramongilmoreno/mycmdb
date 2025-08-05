mycmdb

# Quick start guide

    $ ./env.sh
    $ ./run.sh

Products will be found in the build/ directory.

# Introduction

mycmdb is a personal Configuration (or Content?) Management DataBase.

The core of the tool is a [relational
model](https://en.wikipedia.org/wiki/Relational_model) fed with data from
either static files, or data generated/produced/obtained by a
[Python](https://www.python.org) program.

The data is stored into an internal database (based on [sqlite
3](https://www.sqlite.org)) which is then exploited by _reports_ or
_generators_ that renders the source data into useful products.

# Who is it for?

The user of the mycmdb tool is the one collecting the information, configuring
cmdb and triggering the execution of the tool to generate the products.

If you any of these activities is alien to you, the this tool **is not for
you**.

# What mycmdb is not?

It is not an online service.

It is out of the scope of this project providing an online access to the
features of this tool.

# Useful links

* GitHub repository: https://github.com/ramongilmoreno/mycmdb
* Package in Python Package Index (PyPi): https://pypi.org/project/mycmdb/
* Example project using this package (also in GitHub): https://github.com/ramongilmoreno/mycmdb-test

# Distribution to PyPi

Use these commands to build and publish to pypi.org:

    $ python3 -m build
    $ python3 -m twine upload --repository pypi dist/*

# Changelog

2025-07-19 Support embedded images https://github.com/ramongilmoreno/mycmdb/issues/3
2025-07-21 Support different page format/orientation https://github.com/ramongilmoreno/mycmdb/issues/1
2025-07-28 Support different table cells styles https://github.com/ramongilmoreno/mycmdb/issues/4
2025-08-01 Support Markdown https://github.com/ramongilmoreno/mycmdb/issues/2
2025-08-06 Support custom SQL functions https://github.com/ramongilmoreno/mycmdb/issues/7

