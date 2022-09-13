import logging
import os

from nise.report import oci_create_report
from oci.config import from_file
from oci.config import validate_config
from oci.exceptions import ConfigFileNotFound
from oci.exceptions import InvalidConfig
from oci.exceptions import InvalidKeyFilePath
from oci.exceptions import ProfileNotFound

from sources.source import Source

LOG = logging.getLogger(__name__)


class OCI(Source):
    """Defining the OCI source class."""

    BUCKET = "os.object.bucket-name"
    CONFIG_PROFILE = "NISE_POPULATOR"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.static_file = kwargs.get(self.STATIC_FILE)
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "OCI"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        try:
            config = from_file(
                file_location=os.environ["OCI_CONFIG_FILE"],
                profile_name=self.CONFIG_PROFILE,
            )
            validate_config(config)
            if not config.get(self.BUCKET):
                raise InvalidConfig(
                    {
                        self.BUCKET: f"key missing in your config profile {self.CONFIG_PROFILE}"  # noqa: E501
                    }
                )
            return True
        except (ProfileNotFound):
            LOG.error(
                f"Profile {self.CONFIG_PROFILE} not found in config file {os.environ['OCI_CONFIG_FILE']}"  # noqa: E501
            )
            return False
        except (ConfigFileNotFound, InvalidConfig, InvalidKeyFilePath) as err:
            LOG.error(f"Error : {err}")
            return False

    def _get_bucket_name(self):
        """Return the OCI object storage bucket name"""
        config = from_file(
            file_location=os.environ["OCI_CONFIG_FILE"],
            profile_name=self.CONFIG_PROFILE,
        )
        return config.get(self.BUCKET, "")

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        return True

    def generate(self):
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "oci_bucket_name": self._get_bucket_name(),
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        oci_create_report(options)
