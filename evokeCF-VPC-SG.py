import boto3
import json
import logging

def lambda_handler(event, context):
    
    # Assume-se que o AWS Backup já está configurado e já possui snapshots no vault
    vaultName = "PROD01" # Nome do Vault de Backup
    
    logger = logging.getLogger() # Classe que permite exportar informaçoes para a log do CloudWatch
    logger.setLevel(logging.INFO)
    
    client = boto3.client('cloudformation', region_name="us-east-2")

    response = client.create_stack(
        StackName='VPC-RG-Recovery',
        TemplateURL='https://cloudformation-flavio.s3.us-east-2.amazonaws.com/VPC-SG.YAML',
        #Parametros se houver necessidade
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
        RoleARN="arn:aws:iam::144471715188:role/FullVPC-CloudFormation", #Funçao para acionamento do CloudFormation
        RetainExceptOnCreate=True
    )
    
    waiter = client.get_waiter('stack_create_complete')
    waiter.wait(StackName='VPC-RG-Recovery')

    stack_resources = client.describe_stack_resources(StackName='VPC-RG-Recovery') #Recuperando métricas da implantaçao
    
    logger.info(stack_resources) # Marcas para log do CloudWatch

    for resource in stack_resources['StackResources']: #Recuperando ID da VPC implantada
        if resource['ResourceType'] == 'AWS::EC2::VPC':
            VpcID = resource['PhysicalResourceId']

        if resource['ResourceType'] == 'AWS::EC2::SecurityGroup': #Recuperando ID do SG implantado
            GroupSet = resource['PhysicalResourceId']
            
    logger.info(f"VPCID: {VpcID}, GroupSet: {GroupSet}")

    # Invocando a função Lambda do Job de Backup            
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName='DR-Evoke',
        InvocationType='Event',  # Pode ser 'RequestResponse' ou 'Event' dependendo das suas necessidades
        Payload=json.dumps({ #json necessário para alimentar dados do evento
            "vaultName": vaultName,
            "VpcID": VpcID,
            "GroupSet": GroupSet
        }) 
    )
    
    logger.info(lambda_client)