import abc
import logging
import boto3
from botocore.exceptions import ClientError

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, \
    AWS_S3_ENABLED, AWS_STORAGE_BUCKET_NAME, LOG_LEVEL


logger = logging.getLogger("aws.s3")
logger.setLevel(LOG_LEVEL)


class _ClientS3Interface(object):
    """
    Interface for AWS S3 Client and its dummy equivalent. Children are forced to implement abstract methods.
    It is intended for replacement instantiation depending of the parameters.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def upload_public_file_to_s3(self, local_file, s3_path, mime_type=None):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_remote_file_from_s3(self, s3_path):
        raise NotImplementedError


class DummyClient(_ClientS3Interface):
    """Dummy class that replaces the real client when the service is disabled"""
    message = "Method not run, AWS S3  Client is disabled"

    def upload_public_file_to_s3(self, *args, **kwargs):
        logger.warning(self.message)
        return None

    def delete_remote_file_from_s3(self, *args, **kwargs):
        logger.warning(self.message)
        return None


class ClientS3(_ClientS3Interface):

    def __new__(cls,  *args, **kwargs):
        """
        Returns Dummy Client if service is not enabled.
        :param enabled [optional] overrides Django Configuration
        """

        if not kwargs.get("enabled", AWS_S3_ENABLED):
            return DummyClient()
        else:
            return super(ClientS3, cls).__new__(cls, *args, **kwargs)

    def __init__(self, access_key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY, region=AWS_REGION,
                 bucket=AWS_STORAGE_BUCKET_NAME, enabled=AWS_S3_ENABLED):
        """
        A client for AWS S3, based in boto3's resource interface.

        :param access_key: AWS' access key ID
        :param secret: AWS' secret access key
        :param region: a valid amazon region, f.i. eu-west-1
        :param enabled: If service is not enabled it will instantiate a dummy client, see __new__
        :return: S3 Client or None
        """

        self.session = boto3.session.Session(aws_access_key_id=access_key,
                                             aws_secret_access_key=secret,
                                             region_name=region)
        self.client = self.session.resource("s3")

        try:
            self.client.Bucket(bucket).creation_date

        except ClientError as error:
            if "ResponseMetada" not in error.response:
                logger.error("Bucket %s does not exist", bucket)
                logger.exception(error)
                raise

            status_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 403:
                logger.error(" AWS authentication failed")
            logger.exception(error)
            raise

        self.bucket_name = bucket


    def upload_public_file_to_s3(self, local_file, s3_path, mime_type=None):

        key_name = s3_path
        obj = self.client.Object(self.bucket_name, key_name)

        extra_args = dict()
        extra_args["ACL"] = "public-read"
        if mime_type:
            extra_args["ContentType"] = mime_type

        try:
            obj.upload_file(local_file, ExtraArgs=extra_args)
        except OSError:
            logger.warning("Local file does not exist, upload aborted. File: %s", local_file)
            return None
        except ClientError as error:
            logger.exception(error)
            return None
        url = "https://s3-{region}.amazonaws.com/{bucket}/{key}".format(region=AWS_REGION, bucket=self.bucket_name,
                                                                        key=key_name)
        return url


    def delete_remote_file_from_s3(self, s3_path):
        """
        Deletes an S3 object.

        :param s3_path: A key name of path, must not have trailing slash
        :return:  True if the key does not exist, False if it failed deleting because of a Client error or the object
        was not there.
        """

        obj = self.client.Object(bucket_name=self.bucket_name, key=s3_path)
        try:
            obj.content_length
        except ClientError as error:
            status_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 404:
                logger.debug("Object %s does not exists.", s3_path)
                return False
            raise error

        try:
            obj.delete()
        except ClientError as error:
            logger.exception(error)
            return False
        return True


def get_s3_client(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY, region=AWS_REGION):
    """Helper to get a client fast. Mostly for development and testing"""
    session = boto3.session.Session(aws_access_key_id=key,
                                    aws_secret_access_key=secret,
                                    region_name=region)
    return session.resource("s3")
