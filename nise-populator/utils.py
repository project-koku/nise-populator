import os

import yaml


def load_yaml_file(filename):
    """Local data from yaml file."""
    yamlfile = None
    if filename:
        try:
            with open(filename) as yaml_file:
                yamlfile = yaml.safe_load(yaml_file)
        except TypeError:
            yamlfile = yaml.safe_load(filename)
    return yamlfile


def _get_static_files_path():
    """Return the path to the static-files directory"""
    utils_path = os.path.realpath(__file__)
    module_path = os.path.join(utils_path, os.pardir)
    root_dir = os.path.join(module_path, os.pardir)
    static_files_dir = os.path.normpath(os.path.join(root_dir, "static-files"))
    return static_files_dir


def get_static_file_path(filename):
    """Get file path for file in static files directory."""
    static_files_dir = _get_static_files_path()
    return os.path.join(static_files_dir, filename)
