from boto3 import client
from .storagebase import Storage

class Cloudflare(Storage):

    #initializes a cloudflare object that connects to the service
    def __init__(self, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY, CLOUDFLARE_BUCKET_NAME):
        """Return an authenticated boto3 client connected to Cloudflare R2"""
        account_id = CLOUDFLARE_ACCOUNT_ID
        self.client = client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=CLOUDFLARE_ACCESS_KEY_ID,
            aws_secret_access_key=CLOUDFLARE_SECRET_ACCESS_KEY,
        )
        self.bucket = CLOUDFLARE_BUCKET_NAME

    def put(self, key, body=None, contenttype=None, **kwargs):
        try:
            params = {'Key': key, 'Bucket': self.bucket}
            #accepting optional parameters
            if body is not None:
                params['Body'] = body
            if contenttype is not None:
                params['ContentType'] = contenttype
            params.update(kwargs)
            self.client.put_object(**params)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def get(self, key):
        try:
            response = self.client.get_object(Key=key, Bucket=self.bucket)
            return response
        except Exception as e:
            print(f"Error getting file: {e}")
            return False
    
    def update(self, key, body=None, contenttype=None, **kwargs):
        try:
            params = {'Key': key, 'Bucket': self.bucket}
            #accepting optional parameters
            if body is not None:
                params['Body'] = body
            if contenttype is not None:
                params['ContentType'] = contenttype
            params.update(kwargs)
            self.client.put_object(**params)
            return True
        except Exception as e:
            print(f"Error updating file: {e}")
            return False

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def delete_many(self, keys):
        if not keys:
            return True
        try:
            delete_dict = {'Objects': [{'Key': key} for key in keys]}
            self.client.delete_objects(Bucket=self.bucket, Delete=delete_dict)
            return True
        except Exception as e:
            print(f"Error deleting multiple files: {e}")
            return False
    
    def list_files(self, prefix, file_extension=None):
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
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
        