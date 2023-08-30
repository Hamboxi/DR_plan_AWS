import boto3

#Incluir:
#vmName, vmRegion, vmSize, vmSG,vmImageId

# Crie uma conexão com o serviço CloudFormation usando o cliente do Boto3
cloudformation_client = boto3.client('cloudformation', region_name='us-east-2')

import boto3
from botocore.exceptions import NoCredentialsError

parameters = [
    {
        'ParameterKey': 'vmName',
        'ParameterValue': 'Teste1',
    },
    {
        'ParameterKey': 'vmRegion',
        'ParameterValue': 'us-east-2',
    },
    {
        'ParameterKey': 'vmSize',
        'ParameterValue': 't2.micro',
    },
    {
        'ParameterKey': 'vmSG',
        'ParameterValue': 'sg-0fa29055c5d1d6384',
    },
    {
        'ParameterKey': 'vmImageId',
        'ParameterValue': 'ami-03f38e546e3dc59e1',
    },
]

def generate_s3_presigned_url(bucket_name, object_key, expiration=3600):
    #try:
        s3_client = boto3.client('s3', region_name='us-east-2')
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=expiration
        )
        return url
    #except NoCredentialsError:
    #    return "Credenciais da AWS não configuradas."

# Substitua 'meu-bucket' e 'example.txt' com o nome do seu bucket e objeto
bucket_name = 'cloudformation-flavio'
object_key = 'EC2-DR.YAML'
expiration = 3600  # Tempo de expiração da URL em segundos

presigned_url = generate_s3_presigned_url(bucket_name, object_key, expiration)
print("URL do objeto assinada:", presigned_url)

# Defina os parâmetros da stack

stack_name = 'MinhaStackTeste2'

#with open(presigned_url, 'r') as f:
#    template = f.read()

template = presigned_url

# Crie a stack
response = cloudformation_client.create_stack (
    StackName=stack_name,
    TemplateURL=template,
    Parameters= parameters
)

print("Stack criada:", response)