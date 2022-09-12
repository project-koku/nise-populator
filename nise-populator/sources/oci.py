import logging
import os

from nise.report import oci_create_report
from oci.config import from_file
from oci.config import validate_config
from oci.exceptions import ConfigFileNotFound
from oci.exceptions import InvalidConfig
from oci.exceptions import InvalidKeyFilePath

from sources.source import Source

LOG = logging.getLogger(__name__)


class OCI(Source):
    """Defining the OCI source class."""

    BUCKET = "bucket"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.bucket = kwargs.get(self.BUCKET)
        self.static_file = kwargs.get(self.STATIC_FILE)
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "OCI"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        try:
            if not self.bucket:
                LOG.info("Missing bucket name.")
                return False
            if self.bucket and "OCI_CONFIG_FILE" in os.environ:
                config = from_file(file_location=os.environ["OCI_CONFIG_FILE"])
                validate_config(config)
                return True
        except (ConfigFileNotFound, InvalidConfig, InvalidKeyFilePath) as err:
            LOG.error(f"Error : {err}")
            return False

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        return True

    def generate(self):
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "oci_bucket_name": self.bucket,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        oci_create_report(options)
