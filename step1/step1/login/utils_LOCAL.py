import base64
import getpass
import os
import errno
import socket
import sys
import traceback
import shutil
from django.conf import settings
from paramiko.py3compat import input

import paramiko
from step1.login.models import Image

srcimage_b1_localPath = 0
srcimage_rgb_localPath = 0
rgbimage_b1_localPath = 0

groovyScript = "imageToImage_Registration_cutSource.groovy"
cudaRunDirectory = "cudaPhaseCorrelation/"
roothPath = '/home/giovamt/webAppFolder/imageToImage/'

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
def mk_each_dir(sftp, inRemoteDir, outRemoteDir):
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
	for dirElement in outRemoteDir.split('/'):
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

	currentUserRemoteIn = '/home/giovamt/webAppFolder/imageToImage/users/' + username + '/in/'
	currentUserRemoteOut = '/home/giovamt/webAppFolder/imageToImage/users/' + username + '/out/'
	currentUserRemoteSourceDir = '/home/giovamt/webAppFolder/imageToImage/sources/'

	print currentUserRemoteIn
	print currentUserRemoteOut

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
		mk_each_dir(sftp,currentUserRemoteIn, currentUserRemoteOut)
		print ('after')

		global srcimage_b1_localPath, srcimage_rgb_localPath, rgbimage_b1_localPath; 

		sourceimage_b1 = Image.objects.get(pk=1).sourceImage_b1
		srcimage_b1_localPath = settings.MEDIA_ROOT + '/' + sourceimage_b1.name
		sourceimage_rgb = Image.objects.get(pk=1).sourceImage_rgb
		srcimage_rgb_localPath = settings.MEDIA_ROOT + '/' + sourceimage_rgb.name
		referenceimage_b1 = Image.objects.get(pk=1).referenceImage_b1
		rgbimage_b1_localPath = settings.MEDIA_ROOT + '/' + referenceimage_b1.name

		print srcimage_b1_localPath
		print sourceimage_rgb
		print rgbimage_b1_localPath

		sftp.put(srcimage_b1_localPath, currentUserRemoteIn +'/source_band1.tif')
		sftp.put(srcimage_rgb_localPath, currentUserRemoteIn +'/source_rgb.tif')
		sftp.put(rgbimage_b1_localPath, currentUserRemoteIn +'/reference_band1.tif')

		t.close()

	except Exception as e:
	    print('*** Caught exception: %s: %s' % (e.__class__, e))
	    traceback.print_exc()
	    try:
	        t.close()
	    except:
	        pass
	    sys.exit(1)

def mk_each_dir_local(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise


def test_setup_and_upload(localrootpath=None,username=None):

	print('*** local setup and upload...')

	currentUserLocalIn = localrootpath + 'users/' + username + '/in/'
	currentUserLocalOut = localrootpath + 'users/' + username + '/out/'

	print currentUserLocalIn
	print currentUserLocalOut

	mk_each_dir_local(currentUserLocalIn);
	mk_each_dir_local(currentUserLocalOut);

	global srcimage_b1_localPath, srcimage_rgb_localPath, rgbimage_b1_localPath; 
	sourceimage_b1 = Image.objects.get(pk=1).sourceImage_b1
	srcimage_b1_localPath = settings.MEDIA_ROOT + '/' + sourceimage_b1.name
	sourceimage_rgb = Image.objects.get(pk=1).sourceImage_rgb
	srcimage_rgb_localPath = settings.MEDIA_ROOT + '/' + sourceimage_rgb.name
	referenceimage_b1 = Image.objects.get(pk=1).referenceImage_b1
	rgbimage_b1_localPath = settings.MEDIA_ROOT + '/' + referenceimage_b1.name

	shutil.copyfile(srcimage_b1_localPath, currentUserLocalIn + '/source_band1.tif');
	shutil.copyfile(srcimage_rgb_localPath, currentUserLocalIn + '/source_rgb.tif');
	shutil.copyfile(rgbimage_b1_localPath, currentUserLocalIn + '/reference_band1.tif');

	return currentUserLocalIn;

def setup_configuration_files(currentUserLocalInPath=None, currentUserLocalHomePath=None):
	config_src_filename = currentUserLocalHomePath + 'source.txt'
	config_rfr_filename = currentUserLocalHomePath + 'reference.txt'

	global srcimage_b1_localPath, srcimage_rgb_localPath, rgbimage_b1_localPath 
	
	imageEPSG = Image.objects.get(pk=1).epsg
	print "setup_configuration_files"
	print imageEPSG
	print srcimage_b1_localPath
	print srcimage_rgb_localPath
	print rgbimage_b1_localPath

	config_src = open(config_src_filename, 'w')
	config_src.truncate()
	line1 = srcimage_b1_localPath + "," + str(imageEPSG)
	line2 = srcimage_rgb_localPath + "," + str(imageEPSG)	
	config_src.write(line1)
	config_src.write("\n")
	config_src.write(line2)
	config_src.write("\n")
	config_src.close()

	config_rfr = open(config_rfr_filename, 'w')
	config_rfr.truncate()
	line1 = rgbimage_b1_localPath + "," + str(imageEPSG)
	config_rfr.write(line1)
	config_rfr.close()

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def	run_routine_and_save(currentUsrLocalHomePath = None):
	print "run_routine_and_save"

# 	copy also the groovy script and the cuda routine directory
	srcGroovy = roothPath + "sources/" + groovyScript
	dstGroovy = currentUsrLocalHomePath + groovyScript

	print(srcGroovy, dstGroovy)
	shutil.copyfile(srcGroovy, dstGroovy)

	srcCudadir = roothPath + "sources/" + cudaRunDirectory
	dstCudadir = currentUsrLocalHomePath + cudaRunDirectory

	print(srcCudadir, dstCudadir)

	copyanything(srcCudadir, dstCudadir)
	os.chdir(currentUsrLocalHomePath)
	os.system("groovy " + dstGroovy + " source.txt " + "reference.txt");


