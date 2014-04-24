try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup

def get_package_data():
    return {"ggpylot" : ["exampledata/*.csv"]}

config = {
    "description": "ggplot2 interface in Python via rpy2",
    "author": "Richard Futrell",
    "url": "http://github.mit.edu/futrell/ggpylot",
    "author_email": "futrell@mit.edu",
    "version": "0.0.0.0.0.0.1",
    "install_requires": "pandas rpy2 ".split(),
    "packages": find_packages(),
    "package_dir": {"ggpylot":"ggpylot"},
    "package_data": get_package_data(),
    "scripts": "".split(),
    "name": "ggpylot",
}

setup(**config)
