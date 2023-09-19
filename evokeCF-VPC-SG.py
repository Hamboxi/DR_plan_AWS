import boto3

vaultName = "PROD01"

def lambda_handler(event, context):
    client = boto3.client('cloudformation', region_name="us-east-1")

    response = client.create_stack(
        StackName='VPC-RG-Recovery',
        TemplateURL='https://cloudformation-flavio.s3.us-east-2.amazonaws.com/VPC-SG.YAML',
        #Parameters=[
        #    {
        #        'ParameterKey': 'string',
        #        'ParameterValue': 'string',
        #        'UsePreviousValue': True|False,
        #        'ResolvedValue': 'string'
        #    },
        #],
        DisableRollback=False,
        TimeoutInMinutes=123,
        #NotificationARNs=[
        #    'string',
        #],
        ResourceTypes=[
            'AWS::*',
        ],
        RoleARN="arn:aws:iam::144471715188:role/FullVPC-CloudFormation",
        RetainExceptOnCreate=True
    )
    
    waiter = client.get_waiter('stack_create_complete')
    waiter.wait(StackName='VPC-RG-Recovery')

    stack_resources = client.describe_stack_resources(StackName='VPC-RG-Recovery')

    for resource in stack_resources['StackResources']:
        if resource['ResourceType'] == 'AWS::EC2::VPC':
            VpcID = resource['PhysicalResourceId']

        if resource['ResourceType'] == 'AWS::EC2::SecurityGroup':
            GroupSet = resource['PhysicalResourceId']
    
    return {
        "backup_vault_name": vaultName,
        "VpcID": VpcID,
        "GroupSet": GroupSet
    }