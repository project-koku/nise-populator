import logging
import os
from datetime import datetime
from datetime import timedelta

from nise.report import ocp_create_report

from sources.source import Source


LOG = logging.getLogger(__name__)


class OCP(Source):
    """Defining the OCP source class."""

    CLUSTER_ID = "cluster_id"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.insights_user = os.environ.get("INSIGHTS_USER")
        self.insights_password = os.environ.get("INSIGHTS_PASSWORD")
        self.insights_url = os.environ.get("INSIGHTS_URL")
        self.cluster_id = kwargs.get(self.CLUSTER_ID)
        self.static_file = kwargs.get(self.STATIC_FILE)
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "OCP"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        if self.insights_user and self.insights_password and self.insights_url:
            return True
        return False

    def setup(self):
        """Perform necessary setup."""
        return

    def generate(self):
        """Create data and upload it to the necessary location."""
        self.start_date = datetime.today() - timedelta(days=1)
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "ocp_cluster_id": self.cluster_id,
            "insights_upload": self.insights_url,
            "ros_ocp_info": True,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        ocp_create_report(options)
