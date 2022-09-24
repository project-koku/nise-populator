import logging
import os

from nise.report import gcp_create_report

from sources.source import Source

LOG = logging.getLogger(__name__)


class GCP(Source):
    """Defining the GCP source class."""

    BUCKET = "bucket"
    REPORT_PREFIX = "report_prefix"
    REPORT_NAME = "report_name"
    ETAG = "etag"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.dataset = os.environ.get("GCP_DATASET")
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.etag = kwargs.get(self.ETAG)
        self.bucket = kwargs.get(self.BUCKET)
        self.report_prefix = kwargs.get(self.REPORT_PREFIX, "cur")
        self.static_file = kwargs.get(self.STATIC_FILE)
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "GCP"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        return True

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        return True

    def generate(self):
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gcp_dataset_name": self.dataset,
            "gcp_report_prefix": self.report_prefix,
            "gcp_bucket_name": self.bucket,
            "gcp_etag": self.etag,
            "gcp_resource_level": True,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        gcp_create_report(options)
