
import os, pdb, uuid
import boto3
import botocore
from botocore.exceptions import ClientError
from datetime import date
from fastapi import Depends, HTTPException
from dotenv import load_dotenv

load_dotenv()

today = date.today()
spaces_daily_folder = today.strftime("%b-%d-%Y")

"""Reference Links"""
#https://docs.digitalocean.com/products/spaces/reference/s3-sdk-examples/
#https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html

session = boto3.session.Session()
client = session.client('s3',
                        config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
                        region_name=os.getenv('do_region_name'),
                        endpoint_url=os.getenv('do_endpoint_url'),
                        aws_access_key_id=os.getenv('do_aws_access_key_id'),
                        aws_secret_access_key=os.getenv('do_aws_secret_access_key'))


def create_UUID_folder():
    uuid_folderPath = f'{spaces_daily_folder}/{str(uuid.uuid4())}'

    return uuid_folderPath

def spaces_upload_file(fPath, filename, filesuffix):
    """# Upload a File to a Space"""
    folder_name = create_UUID_folder()
    upload_fname = f'{folder_name}/{filename}{filesuffix}'

    try:
        up = client.upload_file(fPath, # Path to local file
                        os.getenv('do_space_name'),  # Name of Space #os.getenv('do_space_name')
                        upload_fname)  # Name for remote file
        return upload_fname
    except ClientError as e:
        print(e)
        raise HTTPException(status_code=404, detail="Error: Uploading File")

def spaces_presigned_url(upload_fname):
    """# Generate a Pre-Signed URL to Download a Private File"""
    try:
        url = client.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': os.getenv('do_space_name'),
                                                    'Key': upload_fname},
                                            ExpiresIn=3000)
        return url
    except ClientError as e:
        print(e)
        raise HTTPException(status_code=404, detail="Error: Getting uploaded file url")
        #     logging.error(e)
        #     return None

        # # The response contains the presigned URL
        # return response
    #pdb.set_trace()
#     print(url)
# spaces_upload_file()

"""# Get bucket/space name"""

# response = client.list_buckets()
# print(response)
# print('-----------------------------------------------------')
# for space in response['Buckets']:
#     print(space['Name'])

"""# List All Files in a Space"""
# response = client.list_objects(Bucket='apifile')
# for obj in response['Contents']:
#     print(obj['Key'])
