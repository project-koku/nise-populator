import logging
import os
import sys

import yaml

from sources.source_factory import SourceFactory
from utils import get_static_file_path
from utils import load_yaml_file

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
root.addHandler(handler)

LOG = logging.getLogger(__name__)


sources = None
sources_config = os.environ.get("SOURCES_CONFIG")
if sources_config:
    sources = yaml.load(sources_config)
else:
    # Load default sources list
    default_sources_path = get_static_file_path("default_sources.yaml")
    sources = load_yaml_file(default_sources_path)

factory = SourceFactory(sources)
factory.process()
