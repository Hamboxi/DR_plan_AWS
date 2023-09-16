import boto3

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

print("A stack está pronta!")

