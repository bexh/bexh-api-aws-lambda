import subprocess


cmd = "mysql -u user -ppassword -h 127.0.0.1 < scripts/file.sql"
print(cmd)
print(subprocess.getoutput(cmd))


cmd = """
awslocal dynamodb create-table \
    --table-name Tokens \
    --attribute-definitions AttributeName=Uid,AttributeType=N \
    --key-schema AttributeName=Uid,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("table already exists", e)


cmd = """
awslocal dynamodb update-time-to-live \
    --table-name Tokens \
    --time-to-live-specification Enabled=true,AttributeName=TimeToLive
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("error with ttl", e)


cmd = """
awslocal dynamodb put-item \
    --table-name Tokens \
    --item file://scripts/tokens.json
"""
print(cmd)
print(subprocess.getoutput(cmd))

cmd = """
awslocal secretsmanager create-secret \
    --name db-creds \
    --description "Local db creds" \
    --secret-string file://scripts/db-creds.json
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("secret already exists", e)

cmd = """
awslocal sns create-topic \
    --name bet-status-change-email
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)

cmd = """
awslocal sns create-topic \
    --name verification-email
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)

cmd = """
awslocal kinesis create-stream \
    --stream-name exchange-bet \
    --shard-count 1
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)
