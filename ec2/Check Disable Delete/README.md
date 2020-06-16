Check Disable Delete checks AWS instances, off a system that is setup with an IAM role and can read AWS EC2 Tags.

The script looks for a Tag Key called "Name". If the value is not a valid URL, the script will not work. Additionally, 
the script is checking for a page called expired.asp.

If expired.asp is the landing page, then the instance is timestamped and shutdown.

Script is provided as is and is not guaranteed to work for your purposes. Prior to running the script,
ensure the code is understood and tested. This script will shutdown your instances and potentially delete them.

Always ensure you have valid, working, and restorable system backups.