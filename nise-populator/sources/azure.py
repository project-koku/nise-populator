import logging
import os

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from msrestazure.azure_exceptions import ClientException
from msrestazure.azure_exceptions import CloudError
from nise.report import azure_create_report

from sources.source import Source

LOG = logging.getLogger(__name__)


class Azure(Source):
    """Defining the Azure source class."""

    STORAGE_ACCOUNT = "storage_account"
    STORAGE_CONTAINER = "storage_container"
    REPORT_PREFIX = "report_prefix"
    REPORT_NAME = "report_name"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.storage_connection = os.environ.get(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        self.storage_account = kwargs.get(self.STORAGE_ACCOUNT)
        self.storage_container = kwargs.get(self.STORAGE_CONTAINER)
        self.report_prefix = kwargs.get(self.REPORT_PREFIX, "cur")
        self.report_name = kwargs.get(self.REPORT_NAME, "cur")
        self.static_file = kwargs.get(self.STATIC_FILE)
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.storage_connection
        )
        if os.environ.get("AZURE_STORAGE_ACCOUNT") != self.storage_account:
            LOG.error(
                "AZURE_STORAGE_ACCOUNT does not equal storage account in yaml."
            )
        super().__init__(**kwargs)

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "Azure"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        try:
            self.blob_service_client.create_container(self.storage_container)
            return True
        except (ResourceExistsError):
            return True
        except (ClientException, CloudError) as err:
            LOG.info(f"Error: {err}")
            return False

    def _get_existing_objects(self):
        """Return a objects in storage account with the given prefix."""
        container_client = self.blob_service_client.get_container_client(
            self.storage_container
        )
        return container_client.list_blobs(name_starts_with=self.report_prefix)

    def _delete_objects(self, objects_to_delete):
        """Remove list of items from the given storage account."""
        if objects_to_delete:
            container_client = self.blob_service_client.get_container_client(
                self.storage_container
            )
            container_client.delete_blobs(*objects_to_delete)

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        existing_objects = self._get_existing_objects()
        self._delete_objects(existing_objects)

    def generate(self):
        """Create data and upload it to the necessary location."""
        options = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "azure_account_name": self.storage_account,
            "azure_container_name": self.storage_container,
            "azure_prefix_name": self.report_prefix,
            "azure_report_name": self.report_name,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(
                self.static_file, self.start_date, self.end_date
            )
            options["static_report_data"] = static_file_data
        azure_create_report(options)
