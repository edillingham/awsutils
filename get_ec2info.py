import sqlite3
import boto3
import remote_data
import configparser
from pprint import pprint

DEBUG = True

config = configparser.ConfigParser()
config.read('awsutils.ini')

ssh_path = config['awsutils']['ssh_path']
ssh_user = config['awsutils']['ssh_user']
ip_prefix = config['awsutils']['ip_prefix']

print('initializing sql driver')

conn = sqlite3.connect('aws.sqlite3')
conn.row_factory = sqlite3.Row
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

    iid, iip, name = (host.instance_id,
                     host.private_ip_address,
                     next(d['Value'] for d in host.tags if d['Key'] == 'Name'))

    prefix = name.split('.')[0]
    if host.state['Name'] == 'running' and ip_prefix in iip:
        if 'zq' in prefix:
            role = 'zooqueue'
        elif 'fs' in prefix:
            role = 'filestore'
        elif 'dc' in prefix:
            role = 'dc'
        elif 'db' in prefix:
            role = 'database'
        elif 'dev' in prefix or 'beta' in prefix:
            role = 'app'
        else:
            role = 'unknown'
            
        cur.execute('INSERT INTO Servers (instance_id, private_ip, name, role) VALUES (?, ?, ?, ?)', \
                    (iid, iip, name, role))

conn.commit()

results = []

for row in cur.execute("SELECT name, role, private_ip FROM Servers WHERE name LIKE 'ls%' AND role NOT IN ('zooqueue', 'unknown') ORDER BY private_ip"):
    print('querying {role} server named {name} at {private_ip}'.format(**dict(row)))

    d = {'host': row['private_ip']}
    d.update(remote_data.get_php_configs(ssh_path, ssh_user, row['private_ip'], DEBUG))

    results.append(d)

pprint(results)
conn.close()
