import boto3
import sys

accountid = "001122334444"

def region_inventory():
    # Connect to AWS using the credentials provided above or in Environment vars or using IAM role.
    #print 'Connecting with boto3'
    regions = ['us-east-2','us-east-1','us-west-1','us-west-2','ap-northeast-1','ap-northeast-2'
              ,'ap-northeast-3','ap-south-1','ap-southeast-1','ap-southeast-2','ca-central-1'
              ,'cn-north-1','cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','sa-east-1']

    for region in regions:
        ec2client = boto3.client('ec2',region_name=region)

        describe_volumes = ec2client.describe_volumes()
        describe_snapshot = ec2client.describe_snapshots()

        countVolume = 0
        countSnapshot = 0
        availableVolumes = []
        removedVolumes = []
        snapshotsToDelete = []

        print ("Connected to Region: ", region)


        for volume in describe_volumes['Volumes']:
            availableVolumes.append(volume['VolumeId'])
            countVolume = countVolume + 1

        for snapshot in describe_snapshot['Snapshots']:
            if snapshot['OwnerId'] == accountid:
                if snapshot['VolumeId'] not in availableVolumes:
                    if snapshot['Description'] != "" and "ami-" not in snapshot['Description']:
                        countSnapshot = countSnapshot + 1
                        removedVolumes.append(snapshot['VolumeId'])
                        snapshotsToDelete.append(snapshot['SnapshotId'])
                        print "\nSnapshot ID: " + str(snapshot['SnapshotId'])
                        print "Snapshot VolumeID: " + str(snapshot['VolumeId'])
                        print "Snapshot Volume Size: " + str(snapshot['VolumeSize'])
                        print "Snapshot Start Time: " + str(snapshot['StartTime'])
                        print "Snapshot Description: " + str(snapshot['Description'])
                        print "\n"

        print ("Region Summary", region)
        print ("Number of Snapshots that can be Deleted: ", countSnapshot)
        print ("Removed Volumes: ", removedVolumes)
        print ("Snapshots To be Removed: ", snapshotsToDelete)
        print ("\n")

if "__name__" == "__main__"
    region_inventory()
