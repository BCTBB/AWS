SnapshotAwsVolumes.py takes snapshots and can be configured to run/retain snapshots daily, weekly, and monthly basis.

However, the retention, while configurable, will only hold snapshots for a maximum of 7 days. The deletion of snapshots
will only occur if the Name key and value fall within the parameters that are being checked in the conditions.

Make sure you have valid backups and have tested the script in a non-production setting. The script can cause 
irrecoverable damage, if you have not tested and validated it for your purposes.

The script is intended to be a sample of how to leverage the AWS EC2 EBS snapshot api and the publisher is not responsible
for any damages caused by the execution of provided scripts.