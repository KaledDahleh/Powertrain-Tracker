#!/bin/bash
# deploy.sh

# Package Lambda function
zip -r lambda.zip lambda/

# Initialize and apply Terraform
terraform init
terraform apply -auto-approve

# Setup database
python3 database/setup.py

# Deploy scraper to EC2
scp -i key.pem scraper/* ec2-user@${EC2_IP}:~/