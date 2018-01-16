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
	directory = config['enc-checker'].get('Directory')
	if not directory:
		print("You must specify the root directory either with --dir, or in config.ini. Exiting")
		sys.exit(2)

auto_purge = config['enc-checker'].getboolean('AutoPurge', False)
pushover   = config['Pushover'].getboolean('Enabled', False)

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

	for backup in root.iter('Backup'):
		if 'EncryptionState' in backup.attrib:
			print("Backup {0} is encrypted.".format(backup.attrib['JobName']))
		else:
			message = "ALERT! Unencrypted backup job {0}. Full path: {1}.".format(backup.attrib['JobName'], job_full_path)
			print(message)

			if pushover is True:
				data = { 'token': config['Pushover'].get('AppKey'), 'user': config['Pushover'].get('UserKey'), 'message': message }
				r = requests.post('https://api.pushover.net/1/messages.json', data=data)

			if auto_purge is True:
				print("(Not actually...) Proceeding to delete {0}".format(job_full_path))
				# shutil.rmtree(job_full_path)
