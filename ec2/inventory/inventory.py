import boto3
import sys

accountid = "001122334444"

def region_inventory():
    # Connect to AWS using the credentials provided above or in Environment vars or using IAM role.
    #print 'Connecting with boto3'
    regions = ['us-east-2','us-east-1','us-west-1','us-west-2','ap-northeast-1','ap-northeast-2'
               ,'ap-northeast-3','ap-south-1','ap-southeast-1','ap-southeast-2','ca-central-1'
               ,'cn-north-1','cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','sa-east-1']

    try:
        for region in regions:
            ec2resource = boto3.resource('ec2',region_name=region)
            ec2client = boto3.client('ec2',region_name=region)

            describe_volumes = ec2client.describe_volumes()
            describe_snapshot = ec2client.describe_snapshots()
            describe_AMI = ec2client.describe_images()
            describe_instance = ec2client.describe_instances()

            #print describe_snapshot
            countVolume = 0
            countSnapshot = 0
            countAMI = 0

            print ("Connected to Region: ", region)

            for volume in describe_volumes['Volumes']:
                try:
                    countVolume = countVolume + 1
                    if volume['State'] == "available":
                        print "Volume ID: " + volume['VolumeId']
                        print "Volume State: " + volume['State']
                        print "Volume Type: " + volume['VolumeType']
                        print "Volume - Instance Name: Not attached to an instance"
                        print "\n"
                    else:
                        for attachment in volume['Attachments']:
                            for reservation in describe_instance['Reservations']:
                                for instance in reservation['Instances']:
                                    if instance['InstanceId'] == attachment['InstanceId']:
                                        for tag in instance['Tags']:
                                            if tag['Key'] == "Name":
                                                print "Volume ID: " + volume['VolumeId']
                                                print "Volume State: " + volume['State']
                                                print "Volume Type: " + volume['VolumeType']
                                                print "Volume - Instance Name: " + tag['Value']
                                                print "Volume - Instance Launch Time: " + str(instance['LaunchTime'])
                                                print "Volume - Instance ID: " + attachment['InstanceId']
                                                print "Volume - Instance Mount: " + attachment['Device']
                                                print "Volume - Instance State: " + attachment['State']
                                                print "\n"
                except:
                    print "exception thrown: describe_volumes"
                    pass

            for snapshot in describe_snapshot['Snapshots']:
                try:
                    if snapshot['OwnerId'] == accountid:
                        countSnapshot = countSnapshot + 1
                        print "Snapshot ID: " + snapshot['SnapshotId']
                        print "Snapshot Volume Size: " + str(snapshot['VolumeSize'])
                        print "Snapshot Start Time: " + str(snapshot['StartTime'])
                        try:
                            if snapshot['Description'] != "":
                                print "Snapshot Description: " + snapshot['Description']
                            else:
                                print "Snapshot Description: No Description"
                        except:
                            print "trouble describing_snapshot description"
                        print "\n"
                except:
                    print "exception thrown: describe snapshot"
                    pass

            for image in describe_AMI['Images']:
                try:
                    if image['OwnerId'] == accountid:
                        countAMI = countAMI + 1
                        print "Amazon Machine Image ID: " + image['ImageId']
                        print "Amazon Machine Image Location: " + image['ImageLocation']
                        print "Amazon Machine Image State: " + image['State']
                        try:
                            if image['Description'] != "":
                                print "Amazon Machine Image Description: " + image['Description']
                            else:
                                print "Amazon Machine Image does not have a description"
                        except:
                            print "trouble describing_AMI description"
                        print "\n"
                except:
                    print "exception thrown: describe_AMI"
                    pass

            print ("Region Summary", region)
            print ("Number of Volumes: ", countVolume)
            print ("Number of Snapshots: ", countSnapshot)
            print ("Number of AMIs: ", countAMI)
            print ("\n")
    except:
        "The script threw an exception"
        sys.exit()

if "__name__" == "__main__":
    region_inventory()
