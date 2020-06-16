import boto3
import collections
from datetime import datetime, timedelta
import time
import json
import requests
from shutil import copyfile
import os

def checkDisableDelete():
    if os.path.isfile('output/info.json'):
        copyfile('output/info.json', 'input/info.json')
        # backup json
        copyfile('output/info.json', 'output/Backup/info' + time.strftime("%Y%m%d-%H%M%S")+'.json')
    if os.path.isfile('input/info.json'):
        with open('input/info.json') as inp:
            d = json.loads(inp.read())
    else:
        d = {}

    tagName = "foo.foo.foo.randomfoo"
    region = ['us-east-1','us-east-2','ap-southeast-1','ap-southeast-2']

    # Connect to AWS using the credentials provided above or in Environment vars or using IAM role.
    # print 'Connecting with boto3'
    for i in region:
        ec2 = boto3.resource('ec2', region_name=i)

        instances = ec2.instances.filter(Filters=[dict(Name='instance-state-name', Values=['running',
                                                                                           # 'shutting-down',
                                                                                           'terminated',
                                                                                           # 'stopping',
                                                                                           'stopped'
                                                                                           ])])
        #
        for instance in instances:
            for name in instance.state.items():
                if name[0] == "Name":
                    # try:
                    for tag in instance.tags:
                        if tag['Key'] == "Name":
                            if tagName in tag['Value']:
                                if tagName in tag['Value']:
                                    tag2 = ec2.Instance(instance.id).tags
                                    instanceIP = ec2.Instance(instance.id).private_ip_address
                                    instanceState = ec2.Instance(instance.id).state
                                    public_dns = ec2.Instance(instance.id).public_dns_name

                                    hostname = tag['Value']
                                    if hostname not in d:
                                        d[hostname] = {}

                                    for key, value in instanceState.items():
                                        if value == 'running':
                                            d[hostname]['instance_state'] = instanceState
                                            d[hostname]['instance_ip'] = instanceIP
                                            d[hostname]['region'] = i
                                            d[hostname]['Instance_ID'] = instance.id
                                            try:
                                                r = requests.get("https://" + hostname)
                                                # check can be modified to be a different type of health check
                                                # if "expired.asp" in r.url:
                                                if "expired.asp" in r.url:
                                                    d[hostname]['shutdown_timestamp'] = str(datetime.now())
                                                    # stop the instance
                                                    ec2.Instance(instance.id).stop()
                                                    d[hostname]['instance_state']['Name'] = "stopped"
                                                    d[hostname]['instance_state']['Code'] = "80"
                                                else:
                                                    d[hostname]['shutdown_timestamp'] = ''
                                            except:
                                                print "cannot hit https://" + hostname
                                                continue
                                        elif value == 'stopped':
                                            d[hostname]['instance_state'] = instanceState
                                            d[hostname]['instance_ip'] = instanceIP
                                            d[hostname]['region'] = i
                                            d[hostname]['Instance_ID'] = instance.id
                                            ## already stopped
                                            ## check timestamp
                                            ## if greater than 2 weeks, delete
                                            try:
                                                print d[hostname]['shutdown_timestamp']
                                            except:
                                                print "could not print shutdown_timestamp"

                                            if 'shutdown_timestamp' in d[hostname]:
                                                if d[hostname]['shutdown_timestamp'] != '':
                                                    dt = (datetime.now() - datetime.strptime(d[hostname]['shutdown_timestamp'], '%Y-%m-%d %H:%M:%S.%f'))
                                                else:
                                                    d[hostname]['shutdown_timestamp'] = str(datetime.now())
                                                    dt = ''
                                                if dt != '':
                                                    print hostname
                                                    print instance.id
                                                    print ("days", dt.days)
                                                    if dt.days > 14:
                                                        print('terminate')
                                                        # remove route53 entry
                                                        try:
                                                            delete_hostname(hostname, public_dns)
                                                        except:
                                                            print 'Could not delete hostname'

                                                        # once removed,  terminate instance
                                                        ec2.Instance(instance.id).terminate()
                                                        instanceState = ec2.Instance(instance.id).state
                                                        d[hostname]['instance_state'] = instanceState

                                                    else:
                                                        continue
                                            else:
                                                d[hostname]['shutdown_timestamp'] = str(datetime.now())

    data = collections.OrderedDict(sorted(d.items()))

    with open('output/info.json', 'wb') as output:
        json.dump(data, output, indent=4, sort_keys=True)

def changeInstanceState():
    with open('output/info.json') as inp:
        d = json.loads(inp.read())

    for hostname in d:
        if hostname != 'hostname':
            if d[hostname]['instance_state']['Name'] == 'shutting-down' or d[hostname]['instance_state']['Name'] == 'stopped':
                for attributes, sub_attributes in d[hostname].items():
                    if attributes == 'shutdown_timestamp':
                        if d[hostname]['shutdown_timestamp'] != '':
                            dt = (datetime.now() - datetime.strptime(sub_attributes,
                                                                     '%Y-%m-%d %H:%M:%S.%f'))
                            if dt.days > 14:
                                d[hostname]['instance_state']['Name'] = 'terminated'
                                d[hostname]['instance_state']['Code'] = '48'
                            else:
                                d[hostname]['instance_state']['Name'] = 'stopped'
                                d[hostname]['instance_state']['Code'] = '80'

    data = collections.OrderedDict(sorted(d.items()))

    # Remove Empty hostname
    data.pop('hostname', None)

    with open('output/info.json', 'wb') as output:
        json.dump(data, output, indent=4, sort_keys=True)

def delete_hostname(host,pdns):
    r53 = boto3.client('route53')
    # zone_id need to be parameterized
    # zid = 'route53_zoneid'
    zid = 'route53_zoneid'

    try:
        response = r53.change_resource_record_sets(
            HostedZoneId=zid,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': str(host),
                            'Type': 'CNAME',
                            'TTL': 300,
                            'ResourceRecords': [
                                {
                                    'Value': str(pdns)
                                }
                            ]
                        }
                    }
                ]
            })
        print (response)
    except:
        pass

if "__name__" == "__main__":
    checkDisableDelete()
    changeInstanceState()