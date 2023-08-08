"""Module for defining sources."""
import os
from abc import ABC
from abc import abstractmethod
from datetime import datetime

import yaml

from utils import get_static_file_path
from utils import load_yaml_file


class Source(ABC):
    """Defining an abstract class for sources."""

    STATIC_FILE = "static-file"

    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.start_date = datetime.today().replace(day=1, microsecond=0)
        self.end_date = datetime.today().replace(microsecond=0)

    @staticmethod
    @abstractmethod
    def get_source_type():
        """Returns the source type for the factory."""
        pass

    @abstractmethod
    def check_configuration(self):
        """Determine if source is properly configured for access."""
        pass

    @abstractmethod
    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        pass

    @abstractmethod
    def generate(self):
        """Create data and upload it to the necessary location."""
        pass

    @staticmethod
    def obtain_static_file_data(static_file, start_date, end_date):
        """Determine if static file data exists and update contents."""
        static_file_data = None
        env_static_file = os.environ.get(static_file)
        if env_static_file:
            static_file_data = yaml.load(env_static_file)
        else:
            file_path = get_static_file_path(static_file)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                static_file_data = load_yaml_file(file_path)

        if static_file_data:
            for generator_dict in static_file_data.get("generators"):
                for attributes in generator_dict.values():
                    attributes["start_date"] = str(start_date)
                    attributes["end_date"] = str(end_date)
        return static_file_data
