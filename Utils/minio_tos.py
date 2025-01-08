# file_uploader.py MinIO Python SDK example
from minio import Minio
from minio.error import S3Error

def upload(source_file, destination_file):
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        endpoint="yin2du.xin:9000",
        access_key="0VLq5WFevcJ5LHe9g9Ha",
        secret_key="C0Q2sFsMAPJ3q2vHzgwKAhaiXRpB9EbppAjnafUl",
        secure=True,
    )

    # The destination bucket and filename on the MinIO server
    bucket_name = "xnloverservice"

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )

if __name__ == "__main__":
    try:
        source_file = "../requirements.txt"
        destination_file = "requirements.txt"
        upload(source_file, destination_file)
    except S3Error as exc:
        print("error occurred.", exc)