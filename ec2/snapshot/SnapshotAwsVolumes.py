import boto3
from datetime import datetime
import time
import sys
import logging
import argparse

regionArr = []
accountid = "001122334444"

def snapshot(reg, frequency):
    # Connect to AWS using the credentials provided above or in Environment vars or using IAM role.
    regions = reg
    period = frequency

    if frequency == 'day':
        period = 'day'
        date_suffix = datetime.today().strftime('%a')
    elif frequency == 'week':
        period = 'week'
        date_suffix = datetime.today().strftime('%U')
    elif frequency == 'month':
        period = 'month'
        date_suffix = datetime.today().strftime('%b')
    else:
        print('Could not set a date suffix for the snapshot description')
        quit()

    for region in regions:
        ec2resource = boto3.resource('ec2',region_name=region)
        ec2client = boto3.client('ec2', region_name=region)

        describe_volumes = ec2client.describe_volumes()

        volArray = []

        print ("Connected to Region: ", region)

        for volume in describe_volumes['Volumes']:
            for i in volume:
                if i == 'Tags':
                    for i in volume['Tags']:
                        if i['Key'].lower() == "snapshot" and i['Value'].lower() == "true":
                            print "\nVolumeID: " + volume['VolumeId']
                            print "Key: " + i['Key']
                            print "Value: " + i['Value']
                            print "Volume meets requirements"
                            print "Adding Volume ID to snapshot Array"

                            description = '%(period)s_snapshot %(vol_id)s_%(period)s_%(date_suffix)s by snapshot script at %(date)s' % {
                                'period': period,
                                'vol_id': str(volume['VolumeId']),
                                'date_suffix': date_suffix,
                                'date': datetime.today().strftime('%d-%m-%Y %H:%M:%S')
                            }
                            print description

                            try:
                                create_snapshot = ec2resource.Volume(str(volume['VolumeId'])).create_snapshot(Description=str(description))
                                list_nametag = ec2resource.Volume(str(volume['VolumeId'])).tags
                                name = ""
                                for i in list_nametag:
                                    print i
                                    if i['Key'] == "Name":
                                        name = i['Value']

                                voluname = create_snapshot.id
                                create_tags = ec2resource.Snapshot(voluname).create_tags(Tags=[{'Key':'Name','Value':name}])
                                print create_tags
                                volArray.append(str(volume['VolumeId']))
                                time.sleep(2)
                            except Exception, e:
                                print "Unexpected error:", sys.exc_info()[0]
                                # logging.error(e)
                                pass

def snapshotCleanup(reg):
    regions = reg
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        total_deletes = 0

        dt = datetime.datetime.now() - datetime.timedelta(days=6)
        for snap in ec2.snapshots.filter(OwnerIds=[accountid]):
            if "day_snapshot" in snap.description:
                snapshotDate = snap.start_time.replace(tzinfo=None)
                if dt > snapshotDate:
                    try:
                        print ("\nDESCRIPTION: " + snap.description)
                        print ("DELETING " + snap.id)
                        snap.delete()
                        total_deletes = total_deletes + 1
                    except Exception, e:
                        if "ami-" in str(e):
                            print("SKIPPING SNAPSHOT BELONGING TO AMI: " + snap.id)
                        else:
                            print("Probably an API error. Waiting 5 seconds and deleting")
                            time.sleep(5)
                            print ("EXCEPTION ON DELETING: " + snap.id + "\n")
                            print ("DELETING " + snap.id)
                            snap.delete()
                            total_deletes = total_deletes + 1

                        continue
        print("\nNumber of Snapshots Deleted: " + str(total_deletes))

if "__name__" == "__main__":
    parser = argparse.ArgumentParser(description='Snapshot tool arguments')
    parser.add_argument("-r", "--region", default="", type=str,
                        help="Please specify the region to execute in or multiple regions")
    parser.add_argument("-f", "--frequency", default="", type=str,
                        help="Please specify the interval to execute (day, week, month)")

    args = parser.parse_args()
    for idx, val in enumerate(args.region.split(",")):
        regionArr.append(val)

    for idx, val in enumerate(args.frequency.split(",")):
        freq = val

    snapshot(regionArr, freq)
    snapshotCleanup(regionArr)