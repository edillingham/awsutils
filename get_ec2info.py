import sqlite3
import boto3
import remote_data
import configparser

config = configparser.ConfigParser()
config.read('awsutils.ini')

ssh_path = config['awsutils']['ssh_path']
ssh_user = config['awsutils']['ssh_user']
ip_prefix = config['awsutils']['ip_prefix']

conn = sqlite3.connect('aws.sqlite3')
cur = conn.cursor()

print('initializing database')

with open('ec2info.sql', 'r') as f:
    sql = f.read()
    for stmt in sql.split(';'): # sqlite only allows executing one statement at a time
        cur.execute(stmt)

print('fetching server info')

ec2 = boto3.resource('ec2')
for host in ec2.instances.all():
    host.load()

    iid = host.instance_id
    iip = host.private_ip_address
    name = next(d['Value'] for d in host.tags if d['Key'] == 'Name')
    #print(iid, ':', iip, '(', name, ')')

    if host.state['Name'] == 'running' and ip_prefix in iip:
        role = 'app'
        
        if 'zq' in name:
            role = 'zooqueue'
        if 'fs' in name:
            role = 'filestore'
        if 'dc' in name:
            role = 'dc'
        if 'db' in name:
            role = 'database'
            
        cur.execute('INSERT INTO Servers (instance_id, private_ip_address, name, role) VALUES (?, ?, ?, ?)', \
                    (iid, iip, name, role))

conn.commit()

for row in cur.execute("SELECT private_ip_address FROM Servers WHERE name LIKE 'ls%' ORDER BY private_ip_address"):
    d = {'host': row[0]}
    d.update(remote_data.get_php_configs(ssh_path, ssh_user, row[0]))

    print(d)

conn.close()
