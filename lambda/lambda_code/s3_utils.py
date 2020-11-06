"""
A collection of utils and constants for accessing S3 bucket
"""
import boto3
from botocore.exceptions import ClientError

from lambda_code.errors import *

S3_REASON_UPLOAD_USER_PROFILE_IMAGE = 'user_profile_image_upload'
S3_IMAGE_DEST_STR = 'img_dest'

_USER_PROFILE_IMAGES_DIR = 'user_profile_images'
_S3_EXPIRATION_TIME_SECONDS = 300
_S3_BUCKET_NAME = 'wingitdatabucket'


def get_extra_s3_info(username, reason):
    """
    Returns the extra info to return along with the presigned url based on the reason
    """
    if reason == S3_REASON_UPLOAD_USER_PROFILE_IMAGE:
        return True, {
            S3_IMAGE_DEST_STR: "%s/%s_profile_image.png" % (_USER_PROFILE_IMAGES_DIR, username)
        }
    else:
        return False, error(ERROR_UNKNOWN_S3_REASON, reason)


def create_presigned_post(object_name):
    """
    Generate a presigned URL S3 POST request to upload a file

    :param object_name: the file path/name
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(_S3_BUCKET_NAME,
                                                     object_name,
                                                     ExpiresIn=_S3_EXPIRATION_TIME_SECONDS)
    except ClientError as e:
        return False, error(ERROR_UNKNOWN_BOTO3_ERROR, repr(e))

    # The response contains the presigned URL and required fields
    return True, response
