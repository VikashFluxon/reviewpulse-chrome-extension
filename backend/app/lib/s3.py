import os
import boto3

def download_file(bucket, key, local_path):
    client = boto3.client('s3')
    out_path = os.path.join(local_path, os.path.basename(key))
    if not os.path.exists(out_path):
        client.download_file(bucket, key, out_path)
    return out_path