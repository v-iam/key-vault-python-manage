import os
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.resource.resources import ResourceManagementClient

WEST_US = 'westus'
GROUP_NAME = 'azure-sample-group'
KV_NAME = 'keyvault-sample'

# Manage resources and resource groups - create, update and delete a resource group,
# deploy a solution into a resource group, export an ARM template. Create, read, update
# and delete a resource
#
# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
# AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
#
def run_example():
    """Resource Group management example."""
    #
    # Create the Resource Manager Client with an Application (service principal) token provider
    #
    subscription_id = os.environ.get(
        'AZURE_SUBSCRIPTION_ID',
        '11111111-1111-1111-1111-111111111111') # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    kv_client = KeyVaultManagementClient(credentials, subscription_id)
    resource_client = ResourceManagementClient(credentials, subscription_id)

    # You MIGHT need to add KeyVault as a valid provider for these credentials
    # If so, this operation has to be done only once for each credentials
    resource_client.providers.register('Microsoft.KeyVault')

    # Create Resource group
    print('\nCreate Resource Group')
    resource_group_params = {'location': WEST_US}
    print_item(resource_client.resource_groups.create_or_update(GROUP_NAME, resource_group_params))

    # Create a vault
    print('\nCreate a vault')
    vault = kv_client.vaults.create_or_update(
        GROUP_NAME,
        KV_NAME,
        {
            'location': WEST_US,
            'properties': {
                'sku': {
                    'name': 'standard'
                },
                # Fake random GUID
                'tenant_id': '6819f86e-5d41-47b0-9297-334f33d7922d',
                'access_policies': [{
                    'tenant_id': '6819f86e-5d41-47b0-9297-334f33d7922d',
                    'object_id': '6819f86e-5d41-47b0-9297-334f33d7922d',
                    'permissions': {
                        'keys': ['all'],
                        'secrets': ['all']
                    }
                }]
            }
        }
    )
    print_item(vault)

    # Delete Resource group and everything in it
    print('\nDelete Resource Group')
    delete_async_operation = resource_client.resource_groups.delete(GROUP_NAME)
    delete_async_operation.wait()
    print("\nDeleted: {}".format(GROUP_NAME))

def print_item(group):
    """Print an instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))

if __name__ == "__main__":
    run_example()