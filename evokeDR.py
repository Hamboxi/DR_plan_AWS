import boto3
import pandas as pd
import datetime
import logging

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(event) # Marcas para log do CloudWatch
    #Informacoes importantes -----------------------------------------------------------------
    backup_vault_name=event['vaultName']
    VpcID=event['VpcID']
    GroupSet=event['GroupSet']
    #-----------------------------------------------------------------------------------------

    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S") # Obtendo ID única para restore
    id="F"+formatted_date_time

    client = boto3.client('backup') # Instanciando objetos do boto3
    clientec2 = boto3.client('ec2')

    backup_jobs = [] # Listas necessárias para o pandas
    aux = []
    ec2Type = []
    ec2Type2 = []
    result = []

    #Obtendo dados das snapshots do Vault especificado
    backup_jobs = client.list_backup_jobs(
        ByBackupVaultName=backup_vault_name,
        MaxResults=1000 #QUANTIDADE DE SNAPSHOTS
    )

    #Filtrando os Jobs de backup completados
    for job in backup_jobs['BackupJobs']:
        if job['State'] == "COMPLETED":
            aux.append({'BackupJobId': job['BackupJobId'], 'RecoveryPointArn': job['RecoveryPointArn'], 'ArnResource': job['ResourceArn'], 'CreationDate': str(job['CreationDate']), 'vmName': job['ResourceName']})

    # Criando um DataFrame a partir da lista
    df = pd.DataFrame(aux)

    # Filtrando somente a data mais recente de cada key, agrupado por nome de VM
    df = df.groupby('vmName', as_index=False).max()

    dflist = df['vmName'].tolist() #Transformando em lista para listar as VM's

    #client para recuperar dados do ec2 de vms em stopped (Alterar se necessário)
    response3 = clientec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': dflist
            },
            {
                'Name': 'instance-state-name',
                'Values': ['stopped']
            }
        ]
    )
    
    # Extraindo tipo das instâncias que estavam ativas no ec2 e precisam ser recuperadas
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

    i=1
    #client para o restore job
    for index, row in df3.iterrows():
        pointarn = row['RecoveryPointArn']
        instancetype = row['InstanceType']
        name = row['vmName']

        #print("RecoveryPointArn: "+ pointarn+" /InstanceType:"+instancetype)

        # Iterando sobre cada snapshot alvo
        response = client.start_restore_job(
            RecoveryPointArn=pointarn,
            Metadata=
            {
                "Id": id+"-"+str(i),
                "InstanceType": instancetype,
                "VpcId": VpcID, #<-----------------------------------------------Averiguar
                "GroupSet": GroupSet, #<-----------------------------------------------Averiguar
                "Name": name
            },
            IamRoleArn="arn:aws:iam::144471715188:role/ec2-backupRestore", #Funcão necessária para job restore
            CopySourceTagsToRestoredResource=True
        )
        i = i+1 # Mantendo unicidade de ID's
        
        restore_job_id = response['RestoreJobId']
        restore_job_ids = {}
        # Armazenar o ID na lista
        restore_job_ids[name] = restore_job_id
        logger.info(f"Nome: {name}, Restore Job ID: {restore_job_id}")
