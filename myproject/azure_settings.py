# from storages.backends.azure_storage import AzureStorage
from django.conf import settings
from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME # Must be replaced by your <storage_account_name>
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME # Must be replaced by your storage_account_name
    account_key =  settings.AZURE_ACCOUNT_KEY
    azure_container = 'static'
    expiration_secs = None