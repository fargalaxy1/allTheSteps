import base64
import getpass
import os
import socket
import sys
import traceback
from django.conf import settings
from paramiko.py3compat import input

import paramiko
from step1.login.models import Image

def connect_via_SSH_and_ls(hostname=None, username=None, password=None):
	UseGSSAPI = True             # enable GSS-API / SSPI authentication
	DoGSSAPIKeyExchange = True
	port = 22
	# now, connect and use paramiko Client to negotiate SSH2 across the connection
	try:
		client = paramiko.SSHClient()
		print('*** Connecting...')
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.WarningPolicy())
		client.connect(hostname, port, username, password)
		stdin, stdout, stderr = client.exec_command("ls")
		data = stdout.read().splitlines()
		for line in data:
			print line
	except Exception as e:
		print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
    	traceback.print_exc()
    	try:
    		t.close()
    	except:
        	pass

# Set Definition for "mkdir -p"
def mk_each_dir(sftp, inRemoteDir):
    currentDir = '/'
    for dirElement in inRemoteDir.split('/'):
        if dirElement:
            currentDir += dirElement + '/'
            # print('Try to mkdir on :' + currentDir)
            try:
                sftp.mkdir(currentDir)
            except:
            	pass
            	print('%s already exists)' % currentDir)

                # pass # fail silently if remote directory already exists
            
def connect_via_SSH_and_upload(hostname=None, username=None, password=None):

	UseGSSAPI = True             # enable GSS-API / SSPI authentication
	DoGSSAPIKeyExchange = True
	port = 22
	print('*** connect_via_SSH_and_upload...')

	userRemoteInFolder = '/nfs/staging/giovamt/gpugateway/' + username + '/in/imageRegistration'

	print userRemoteInFolder
	# get host key, if we know one
	hostkeytype = None
	hostkey = None
	try:
		host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
	except IOError:
		try:
		# try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
		    host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
		except IOError:
		    print('*** Unable to open host keys file')
		    host_keys = {}

	if hostname in host_keys:
		hostkeytype = host_keys[hostname].keys()[0]
		hostkey = host_keys[hostname][hostkeytype]
		print('Using host key of type %s' % hostkeytype)

	try:
		t = paramiko.Transport((hostname, port))
		t.connect(hostkey, username, password)
		sftp = paramiko.SFTPClient.from_transport(t)
		# copy this demo onto the server
		mk_each_dir(sftp,userRemoteInFolder)
		print ('after')
		sourceimage_b1 = Image.objects.get(pk=1).sourceImage_b1
		srcimage_b1_localPath = settings.MEDIA_ROOT + '/' + sourceimage_b1.name
		sourceimage_rgb = Image.objects.get(pk=1).sourceImage_rgb
		srcimage_rgb_localPath = settings.MEDIA_ROOT + '/' + sourceimage_rgb.name
		referenceimage_b1 = Image.objects.get(pk=1).referenceImage_b1
		rgbimage_b1_localPath = settings.MEDIA_ROOT + '/' + referenceimage_b1.name

		print srcimage_b1_localPath
		print sourceimage_rgb
		print rgbimage_b1_localPath

		sftp.put(srcimage_b1_localPath, userRemoteInFolder +'/source_band1.tif')
		sftp.put(srcimage_rgb_localPath, userRemoteInFolder +'/source_rgb.tif')
		sftp.put(rgbimage_b1_localPath, userRemoteInFolder +'/reference_band1.tif')

	    # sftp.get('demo_sftp_folder/README', 'README_demo_sftp')
		t.close()

	except Exception as e:
	    print('*** Caught exception: %s: %s' % (e.__class__, e))
	    traceback.print_exc()
	    try:
	        t.close()
	    except:
	        pass
	    sys.exit(1)
