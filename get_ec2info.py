import sqlite3
import boto3

conn = sqlite3.connect('aws.sqlite3')
cur = conn.cursor()

print('initializing database')

with open('ec2info.sql', 'r') as f:
    sql = f.read()
    for stmt in sql.split(';'): # sqlite only allowed executing one statement at a time
        cur.execute(stmt)

print('fetching server info')

ec2 = boto3.resource('ec2')
for host in ec2.instances.all():
    host.load()

    iid = host.instance_id
    iip = host.private_ip_address
    name = next(d['Value'] for d in host.tags if d['Key'] == 'Name')
    #print(iid, ':', iip, '(', name, ')')
    
    cur.execute('INSERT INTO Servers (instance_id, private_ip_address, name) VALUES (?, ?, ?)', (iid, iip, name))

conn.commit()

for row in cur.execute("SELECT * FROM Servers ORDER BY name"):
    print(row)

conn.close()
