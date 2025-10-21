from boto3 import client
import os

def create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY) -> client:
    """Return an authenticated boto3 client connected to Cloudflare R2"""
    account_id = CLOUDFLARE_ACCOUNT_ID
    return client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=CLOUDFLARE_ACCESS_KEY_ID,
        aws_secret_access_key=CLOUDFLARE_SECRET_ACCESS_KEY,
    )

def upload_file(s3_client, file_name, bucket, object_name=None):
    try:
        s3_client.upload_file(file_name, bucket, object_name or file_name)
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

def download_file(s3_client, bucket, object_name, file_name):
    try:
        s3_client.download_file(bucket, object_name, file_name)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False
def delete_file(s3_client, bucket, object_name):
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_name)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
def list_files(s3_client, bucket, prefix, file_extension):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' in response:
            if file_extension:
                files = []
                for file in response['Contents']:
                    key = file['Key']
                    if key.endswith(file_extension):
                        key = key.replace(prefix, "")
                        key = key.replace(file_extension, "")
                        key = key.replace("/", "")
                        files.append(key)
                return files

            else: 
                return [item['Key'] for item in response['Contents']]
        else:
            return []
    except Exception as e:
        print(f"Error listing files: {e}")
        return []