import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # Cria um cliente para o serviço AWS Backup
    backup_client = boto3.client('backup')
    
    # Lista os planos de backup
    backup_plans = backup_client.list_backup_plans()['BackupPlansList']
    
    # Encontra o plano de backup para as máquinas EC2
    ec2_backup_plan = next(plan for plan in backup_plans if plan['BackupPlanName'] == 'EC2 Backup Plan')
    
    # Lista as seleções de recursos para o plano de backup das máquinas EC2
    resource_selections = backup_client.list_backup_selections(BackupPlanId=ec2_backup_plan['BackupPlanId'])['BackupSelectionsList']
    
    # Encontra a seleção de recursos para as máquinas EC2
    ec2_resource_selection = next(selection for selection in resource_selections if selection['SelectionName'] == 'EC2 Resource Selection')
    
    # Lista os backups mais recentes para a seleção de recursos das máquinas EC2
    ec2_backups = backup_client.list_recovery_points_by_backup_vault(BackupVaultName=ec2_resource_selection['BackupVaultName'], ByResourceType='EC2')['RecoveryPoints']

    # Encontra a data mais recente dos backups
    latest_backup_date = max(datetime.strptime(backup['CompletionDate'], '%Y-%m-%dT%H:%M:%S.%fZ') for backup in ec2_backups)
    
    # Filtra os backups pela data mais recente
    latest_ec2_backups = [backup for backup in ec2_backups if datetime.strptime(backup['CompletionDate'], '%Y-%m-%dT%H:%M:%S.%fZ') == latest_backup_date]
    
    # Cria um cliente para o serviço EC2
    ec2_client = boto3.client('ec2')
    
    # Cria AMIs a partir dos backups mais recentes das máquinas EC2
    for backup in latest_ec2_backups:
        ec2_client.create_image(InstanceId=backup['ResourceId'], Name=f"AMI from backup {backup['RecoveryPointArn']}", NoReboot=True)

        