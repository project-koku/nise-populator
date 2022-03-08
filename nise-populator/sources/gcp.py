import logging
import os

import boto3
from botocore.exceptions import ClientError
from nise.report import gcp_create_report

from sources.source import Source

LOG = logging.getLogger(__name__)

# TODO: I think nise will need the GOOGLE_APPLICATION_CREDENTIALS
# to upload to the container.

class GCP(Source):
    """Defining the AWS source class."""

    DATASET = "dataset"
    PROJECT_ID = "project_id"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.dataset = os.environ.get("GCP_DATASET")
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "GCP"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        # TODO: See if we have bigquery
        return True

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        return True

    def generate(self):
        """Create data and upload it to the necessary location."""
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gcp_dataset_name": self.dataset,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        gcp_create_report(options)
