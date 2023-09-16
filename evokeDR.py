import boto3
import pandas as pd
import datetime

now = datetime.datetime.now()

formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

#ALTERE O ID APÓS CADA EXECUÇÃO
id="F"+formatted_date_time

client = boto3.client('backup')
clientec2 = boto3.client('ec2')

backup_jobs = []
aux = []
ec2Type = []
ec2Type2 = []
result = []

#Vault Target
backup_vault_name = 'PROD01'

backup_jobs = client.list_backup_jobs(
    ByBackupVaultName=backup_vault_name,
    MaxResults=1000 #QUANTIDADE DE SNAPSHOTS
)

#Filtrando os BackupJobs completos
for job in backup_jobs['BackupJobs']:
    if job['State'] == "COMPLETED":
        aux.append({'BackupJobId': job['BackupJobId'], 'RecoveryPointArn': job['RecoveryPointArn'], 'ArnResource': job['ResourceArn'], 'CreationDate': str(job['CreationDate']), 'vmName': job['ResourceName']})

# Criando um DataFrame a partir da lista
df = pd.DataFrame(aux)

# Filtrando somente a data mais recente de cada key
df = df.groupby('vmName', as_index=False).max()

dflist = df['vmName'].tolist() #Transformando em lista para listar as VM's

#client para recuperar tipo de instancia
response3 = clientec2.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': dflist
        }
    ]
)

for instance in response3['Reservations']:
    for instanceType in instance['Instances']:
        auxType = instanceType['InstanceType']
        for tags in instanceType['Tags']:
            if tags['Key'] == 'Name':
                ec2Type.append({
                    'vmName': tags['Value'],
                    'InstanceType': auxType
                }) #Tipo de instância

ec2Type = pd.DataFrame(ec2Type)

#Concatenar RecoveryPointArn com InstanceType
df3 = ec2Type.merge(df, on='vmName', how='inner')

df3 = df3.drop_duplicates(subset='vmName')

print (df3)

i=1
#client para o restore job
for index, row in df3.iterrows():
    pointarn = row['RecoveryPointArn']
    instancetype = row['InstanceType']
    name = row['vmName']

    #print("RecoveryPointArn: "+ pointarn+" /InstanceType:"+instancetype)

    # Chamar a função start_restore_job
    response = client.start_restore_job(
        RecoveryPointArn=pointarn,
        Metadata=
        {
            "Id": id+"-"+str(i),
            "InstanceType": instancetype,
            "VpcId": "vpc-0c3a76d28ef14c101",
            "GroupSet": "sg-0c900dbc8a39d3296",
            "Name": name
        },
        IamRoleArn="arn:aws:iam::144471715188:role/ec2-backupRestore",
        CopySourceTagsToRestoredResource=True
    )
    print("ID-"+name+": "+id+"-"+str(i))
    i = i+1