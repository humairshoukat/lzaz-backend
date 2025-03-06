import os
from azure.storage.blob import BlobServiceClient
import random
import string
from django.core.mail import send_mail
from django.conf import settings


# Load Azure Blob Storage credentials from environment variables
AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_KEY = os.getenv('AZURE_STORAGE_KEY')
AZURE_BLOB_CONTAINER_NAME = os.getenv('AZURE_BLOB_CONTAINER_NAME')


# Construct the Blob Service Client
connection_string = f"DefaultEndpointsProtocol=https;AccountName={AZURE_STORAGE_ACCOUNT_NAME};AccountKey={AZURE_STORAGE_KEY};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


def save_file_to_blob(file):
    try:
        file_name = file.name
        blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONTAINER_NAME, blob=f"lzaz-pim/{file_name}")
        blob_client.upload_blob(file, overwrite=True)
        file_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_BLOB_CONTAINER_NAME}/lzaz-pim/{file_name}"
        print(f"File {file_name} uploaded successfully to Azure Blob Storage")
        print()
        return file_url
    except Exception as e:
        print("Error uploading file to Azure Blob Storage:", str(e))
        return None


def delete_file_from_blob(file_url):
    try:
        # Extract the file name from the URL
        file_name = file_url.split('/')[-1]
        blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONTAINER_NAME, blob=f"lzaz-pim/{file_name}")
        blob_client.delete_blob()
        print(f"File {file_name} successfully deleted from Azure Blob Storage")
    except Exception as e:
        print(f"Error deleting file from Azure Blob Storage: {e}")


def generate_random_string(length=30):
    characters = string.ascii_letters  # Includes both lowercase and uppercase letters

    # Generate the random string using only the letters
    return ''.join(random.choice(characters) for _ in range(length))


def send_email(subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list
        )
        return True
    except Exception as e:
        print("Error sending email: ", str(e))
        return False
