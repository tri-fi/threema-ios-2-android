# Threema iOS to Android Migration

This python tool/script can be used to migrate an iOS Threema database to Android.
Even though the script takes over the "heavy" work, it still requires some manual
actions.

## Warning
Early version, not heavily tested.  
Other messages than text are currently not migrate-able by this script.

## Progress

### Currently Working
- Contacts
- Groups
- Private Chats
- Group Chats

### Not Working
- Any other messages than text messages (images, gifs, audiomessage, etc.)


## Procedure

### Create unencrypted iOS Backup with iTunes
Use iTunes to create an **unencrypted** backup of your device, where Threema is
installed on.

### Extract Threema Database and Files from the Backup
Use a tool like [iBackup Viewer](https://www.imactools.com/iphonebackupviewer/)
to extract the required files. This tool is free for unencrypted backups.  
You find them in the following "directory": **AppDomainGroup-group.ch.threema** and
from the you need the `ThreemaData.sqlite` file and the `.ThreemaData_SUPPORT`
directory.  
Save both files somewhere on your disk and use the path to the sqlite file as first
argument for the python script.

### Run the Python Script
Run the `main.py` script with the path to the sqlite-database as first argument.
Optionally, you can give a second argument with a path to where the output should
be stored (by default in a `output` directory).  
After the script finished you'll find csv files in the output directory containing
contacts, groups and chats.

### Create Android Backup
Configure Threema with the same ID (!) on your (new) Android device (you can use
Threema Safe to transfer your ID (without chats) from iOS to Android).  
Then, create a backup within Android. Copy it to your pc and un-zip it with the
password you set during the backup configuration.

### Migration
Copy (and replace) everything from the `output` folder (step before last step)
into the un-zipped back folder. Zip the content (not the directory) of the
android backup again (using any password) and copy it on your phone.  

### Import Backup
On your Android device reset Threema again and start configuring it again. Upon
first start, select to restore backup and select the backup zip file you created
in the previous steps.

