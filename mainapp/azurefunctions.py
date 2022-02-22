from azure.storage.blob import BlobServiceClient,ContentSettings,ContainerClient,PublicAccess
from django.conf import settings

def upload_medical_files_cloud(uploadfile,uploadfilename,uploadmime):
    """
        files - file in InMemoryUploadedFile
        filename - file name
        type - type of the file to upload
        storage_container_name - Container name in which files will be uploaded
        blob_name - Blob name is the filename which is uploaded
    """
    try:
        files = uploadfile
        blob_name = uploadfilename
        upload_content_type = uploadmime
        storage_container_name = 'medicalrecords'
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        create_container_client = ContainerClient.from_connection_string(conn_str=settings.AZURE_CONNECTION_STRING, container_name=storage_container_name)
        """
            Checking if the continer exists.If not, create it and set the container_client variable
        """
        if create_container_client.exists() == False:
            create_container_client.create_container(public_access=PublicAccess.Blob)  

        container_client = blob_service_client.get_container_client(storage_container_name)
        blob_client = container_client.get_blob_client(blob_name)

        image_content_setting = ContentSettings(content_type=upload_content_type)

        blob_client.upload_blob(files, blob_type="BlockBlob", content_settings=image_content_setting)
        data = {
            "url" : blob_client.url,
            "success" : True,
            "error" : None
        }
        return data
    except Exception as e:
        print(str(e))
        data = {
            "url" : "",
            "success" : False,
            "error" : str(e)
        }
        return data
