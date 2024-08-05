"""A factory to create sources from a configuration."""

import logging
import os

from sources.aws import AWS
from sources.azure import Azure
from sources.gcp import GCP
from sources.oci import OCI
from sources.ocp import OCP

LOG = logging.getLogger(__name__)


class SourceFactory:
    """Create sources from provided source configuration."""

    def __init__(self, source_config):
        """Initialize the factory with source configuration."""
        self.source_config = source_config
        self.valid_sources = self._create_valid_sources_list()
        self.valid_source_map = {}
        for valid_source in self.valid_sources:
            self.valid_source_map[valid_source.get_source_type()] = (
                valid_source
            )
        self.sources = self._process_config()
        super().__init__()

    def _create_valid_sources_list(self):
        """Create a list of valid sources."""
        comma_separate_sources = os.environ.get("POPULATE_SOURCES")
        if not comma_separate_sources:
            return [AWS, Azure, OCP, GCP, OCI]
        valid_sources = []
        sources_mapping = {
            "aws": AWS,
            "azure": Azure,
            "ocp": OCP,
            "gcp": GCP,
            "oci": OCI,
        }
        for provider_substring in comma_separate_sources.split(","):
            key = provider_substring.lower().replace(" ", "")
            if source_class := sources_mapping.get(key):
                valid_sources.append(source_class)
        LOG.debug(f"Populating sources: {valid_sources}")
        return valid_sources

    def _process_config(self):
        """Create sources based on the source configuration."""
        sources = []
        if not self.source_config:
            return sources

        sources_list = self.source_config.get("sources", [])
        for source in sources_list:
            for source_data in source.values():
                if source_data.get("type") in self.valid_source_map.keys():
                    source_class = self.valid_source_map[
                        source_data.get("type")
                    ]
                    initialized_source = source_class(**source_data)
                    sources.append(initialized_source)
        return sources

    def process(self):
        """Process all initialized sources."""
        for source in self.sources:
            try:
                if source.check_configuration():
                    source.setup()
                    source.generate()
            except Exception:
                LOG.exception("Data generation error occcurred.")
