import logging
import os
from datetime import datetime
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from nise.report import aws_create_report

from sources.source import Source

LOG = logging.getLogger(__name__)


class AWS(Source):
    """Defining the AWS source class."""

    BUCKET = "bucket"
    REPORT_PREFIX = "report_prefix"
    REPORT_NAME = "report_name"

    def __init__(self, **kwargs):
        """Initialize the source with configuration data."""
        self.kwargs = kwargs
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.s3_bucket = kwargs.get(self.BUCKET)
        self.s3_report_prefix = kwargs.get(self.REPORT_PREFIX, "cur")
        self.s3_report_name = kwargs.get(self.REPORT_NAME, "cur")
        self.static_file = kwargs.get(self.STATIC_FILE)
        self.credentials = {
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret,
        }
        self.s3_client = boto3.client("s3", **self.credentials)
        super().__init__()

    @staticmethod
    def get_source_type():
        """Returns the source type for the factory."""
        return "AWS"

    def check_configuration(self):
        """Determine if source is properly configured for access."""
        try:
            return self.s3_client.head_bucket(Bucket=self.s3_bucket)
        except ClientError as err:
            LOG.info(f"Error: {err}")
            return False

    def _get_existing_objects(self):
        """Return a list of objects in bucket with the given prefix."""
        objects = None
        response = self.s3_client.list_objects(
            Bucket=self.s3_bucket, Prefix=self.s3_report_prefix
        )
        if response.get("Contents"):
            objects = [
                item.get("Key") for item in response.get("Contents", [])
            ]
        return objects

    def _delete_objects(self, objects_to_delete):
        """Remove list of items from the given s3 bucket."""
        LOG.info(
            f"s3_bucket={self.s3_bucket} objects_to_delete={objects_to_delete}"
        )
        if objects_to_delete:
            object_list = [{"Key": obj_name} for obj_name in objects_to_delete]
            self.s3_client.delete_objects(
                Bucket=self.s3_bucket, Delete={"Objects": object_list}
            )

    def setup(self):
        """Perform necessary setup, like cleaning up existing objectstorage."""
        existing_objects = self._get_existing_objects()
        self._delete_objects(existing_objects)

    def generate(self):
        """Create data and upload it to the necessary location."""
        options = {
            "start_date": datetime.today().replace(day=1),
            "end_date": datetime.today() + timedelta(days=1),
            "aws_bucket_name": self.s3_bucket,
            "aws_prefix_name": self.s3_report_prefix,
            "aws_report_name": self.s3_report_name,
        }
        if self.static_file:
            static_file_data = Source.obtain_static_file_data(self.static_file)
            options["static_report_data"] = static_file_data
        aws_create_report(options)
