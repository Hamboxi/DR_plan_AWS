#!/bin/bash

# Defina os parâmetros da função Lambda
function_name="VPC-SG-CloudFormation"
input_payload={\"key1": \"value1",\"key2": \"value2"} 
# Substitua pelos dados que você deseja enviar para a função

# Comando para invocar a função Lambda
aws lambda invoke --function-name "$function_name" --payload "$input_payload" output.json

# Verifique a saída (output.json)
cat output.json