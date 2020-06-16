import boto3
import collections
import json

d = {}
currentregion = ['us-east-2','us-east-1','us-west-1','us-west-2','ap-northeast-1','ap-northeast-2'
                ,'ap-northeast-3','ap-south-1','ap-southeast-1','ap-southeast-2','ca-central-1'
                ,'cn-north-1','cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','sa-east-1']

def queryAWS():
    print "Hostname" \
          ",Region" \
          ",InstanceId" \
          ",InstanceType" \
          ",InstanceState" \
          ",PrivateDnsName" \
          ",PublicDnsName" \
          ",PrivateIpAddress" \
          ",PublicIpAddress"
    for cr in currentregion:
        try:
            client = boto3.client('ec2',region_name=cr)
            response = client.describe_instances()
            for r in response['Reservations']:
                for i in r['Instances']:
                    for t in i['Tags']:
                        if t['Key'] == "Name":
                            hostname = str(t['Value'])
                            d[hostname] = {}
                            d[hostname]['Region'] = cr
                    d[hostname]['InstanceId'] = i['InstanceId']
                    d[hostname]['InstanceType'] = i['InstanceType']
                    d[hostname]['PrivateDnsName'] = i['PrivateDnsName']
                    d[hostname]['PublicDnsName'] = i['PublicDnsName']
                    for ck, cv in i['State'].iteritems():
                        if ck == "Name":
                            d[hostname]['InstanceState'] = cv
                    try:
                        d[hostname]['PrivateIpAddress'] = i['PrivateIpAddress']
                    except:
                        d[hostname]['PrivateIpAddress'] = "NULL"
                    try:
                        d[hostname]['PublicIpAddress'] = i['PublicIpAddress']
                    except:
                        d[hostname]['PublicIpAddress'] = "NULL"
                    for e in i['BlockDeviceMappings']:
                        d[hostname]['DeviceName'] = e['DeviceName']
                        for ek, ev in e['Ebs'].iteritems():
                            if ek == "VolumeId":
                                d[hostname]['VolumeId'] = ev
                            elif ek == "Status":
                                d[hostname]['VolumeStatus'] = ev
                    print hostname \
                          + "," + d[hostname]['Region'] \
                          + "," + d[hostname]['InstanceId'] \
                          + "," + d[hostname]['InstanceType'] \
                          + "," + d[hostname]['InstanceState'] \
                          + "," + d[hostname]['PrivateDnsName'] \
                          + "," + d[hostname]['PublicDnsName'] \
                          + "," + d[hostname]['PrivateIpAddress'] \
                          + "," + d[hostname]['PublicIpAddress']
        except:
            pass

    writeFile()

def writeFile():
    data = collections.OrderedDict(sorted(d.items()))

    with open('output/inventoryinfo.json', 'wb') as output:
        json.dump(data, output, indent=4, sort_keys=True)

if __name__ == '__main__':
    queryAWS()