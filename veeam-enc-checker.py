import argparse
import configparser
from glob import glob
import os.path
import requests
import shutil
import sys
import xml.etree.ElementTree as etree

parser = argparse.ArgumentParser()
parser.add_argument("--dir", help="The directory to search for VBM files", type=str)
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.ini')

if args.dir:
    directory = args.dir
else:
    try:
        directory = config['enc-checker'].get('Directory')
    except:
        print("You must specify the root directory either with --dir, or in config.ini. Exiting")
        sys.exit(2)

auto_purge = config['enc-checker'].getboolean('AutoPurge', False)
pushover   = config['Pushover'].getboolean('Enabled', False)


def alert(job_name, job_full_path):
    if pushover is True:
        data = { 'token': config['Pushover'].get('AppKey'), 'user': config['Pushover'].get('UserKey'), 'message': message }
        r = requests.post('https://api.pushover.net/1/messages.json', data=data)

    if auto_purge is True:
        print("(Not actually...) Proceeding to delete {0}".format(job_full_path))
        # shutil.rmtree(job_full_path)
    
    return True

print("Searching for VBM files in:  {0}".format(directory))
print("Auto purge enabled:          {0}".format(auto_purge))
print("")

vbms = glob(directory + '/**/*.vbm', recursive=True)

for vbm in vbms:
    vbm_full_path = os.path.abspath(vbm)
    job_full_path = os.path.dirname(vbm_full_path)

    print("Checking VBM file '{0}'".format(vbm_full_path))
    tree = etree.parse(vbm)
    root = tree.getroot()

    job_name = root.findall('Backup')[0].attrib['JobName']
    storages = root.findall("./BackupMetaInfo/Storages/Storage")

    alert_sent = False

    for s in storages:
        if s.attrib['StorageCryptoKeyIdTag'] == '00000000-0000-0000-0000-000000000000':
            alert_sent = alert(job_name, job_full_path)
            break
    
    if alert_sent is False:
        print(f"Backup {job_name} is encrypted.")
    else:
        print(f"ALERT: Backup {job_name} is NOT encrypted")