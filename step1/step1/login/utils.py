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
from step1.login.models import SSHCredentials

srcimage_b1_localPath = 0
srcimage_rgb_localPath = 0
rgbimage_b1_localPath = 0

groovyScript = "imageToImage_Registration_cutSource.groovy"
cudaRunDirectory = "cudaPhaseCorrelation/"
roothPath = '/nfs/staging/giovamt/WebAppFolder/imageToImage/'

def copyRunCode_and_set_conf_files_inRemoteHost(currentUserName= None, hostname=None, username=None, password=None):
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
		
		currentUserLocalHomePath = roothPath + 'users/' + currentUserName + '/'

		sourcesPath = roothPath + 'sources/'
		cudaDirPath = sourcesPath + cudaRunDirectory
		copyRunSourcesCommand = 'cp -r ' + cudaDirPath +  ' ' + currentUserLocalHomePath + cudaRunDirectory 

		stdin, stdout, stderr = client.exec_command(copyRunSourcesCommand)

		srcGroovyScript = sourcesPath + groovyScript
		dstGroovyScript = currentUserLocalHomePath + groovyScript
		copyGroovyScriptCommand = 'cp -r ' + srcGroovyScript +  ' ' + dstGroovyScript
		stdin, stdout, stderr = client.exec_command(copyGroovyScriptCommand)
		client.close()


	except Exception as e:
		print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
    	traceback.print_exc()
    	try:
    		client.close()
    	except:
        	pass

# Set Definition for "mkdir -p"
def mk_each_dir(sftp, remoteDir):
	currentDir = '/'
	for dirElement in remoteDir.split('/'):
		if dirElement:
			currentDir += dirElement + '/'
			#print('Try to mkdir on :' + currentDir)
			try:
				sftp.mkdir(currentDir)
			except:
				pass
			#print('%s already exists)' % currentDir)
			
			pass # fail silently if remote directory already exists
            
def remoteHost_Setup_and_upload(currentUserName= None, hostname=None, username=None, password=None):

	UseGSSAPI = True             # enable GSS-API / SSPI authentication
	DoGSSAPIKeyExchange = True
	port = 22
	print('*** remoteHost_Setup_and_upload...')

	currentUserRemoteIn = roothPath + 'users/' + currentUserName + '/in/'
	currentUserRemoteOut = roothPath + 'users/' + currentUserName + '/out/'
	#currentUserRemoteSourceDir = '/home/giovamt/webAppFolder/imageToImage/sources/'

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

		mk_each_dir(sftp,currentUserRemoteIn)
		mk_each_dir(sftp,currentUserRemoteOut)

		print ('after')

		global srcimage_b1_localPath, srcimage_rgb_localPath, rgbimage_b1_localPath; 

		sourceimage_b1 = Image.objects.get(pk=1).sourceImage_b1
		srcimage_b1_localPath = settings.MEDIA_ROOT + '/' + sourceimage_b1.name
		sourceimage_rgb = Image.objects.get(pk=1).sourceImage_rgb
		srcimage_rgb_localPath = settings.MEDIA_ROOT + '/' + sourceimage_rgb.name
		referenceimage_b1 = Image.objects.get(pk=1).referenceImage_b1
		rgbimage_b1_localPath = settings.MEDIA_ROOT + '/' + referenceimage_b1.name

		sftp.put(srcimage_b1_localPath, currentUserRemoteIn +'source_band1.tif')
		sftp.put(srcimage_rgb_localPath, currentUserRemoteIn +'source_rgb.tif')
		sftp.put(rgbimage_b1_localPath, currentUserRemoteIn +'reference_band1.tif')

		currentUserLocalDir = settings.USRDIR_ROOT + '/'
		imageSrc1_remotePath = currentUserRemoteIn +'source_band1.tif'
		imageSrc2_remotePath = currentUserRemoteIn +'source_rgb.tif'
		imageRfr_remotePath = currentUserRemoteIn +'reference_band1.tif'

		setup_configuration_files(currentUserLocalDir, imageSrc1_remotePath, imageSrc2_remotePath, imageRfr_remotePath)
		
		local_config_src_filename = currentUserLocalDir + 'source.txt'
		local_config_rfr_filename = currentUserLocalDir + 'reference.txt'

		remote_config_src_filename = roothPath + 'users/' + currentUserName + '/' + 'source.txt'
		remote_config_rfr_filename = roothPath + 'users/' + currentUserName + '/' + 'reference.txt'

		sftp.put(local_config_src_filename, remote_config_src_filename)
		sftp.put(local_config_rfr_filename, remote_config_rfr_filename)

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



def setup_configuration_files(currentUserLocalDir=None, imageSrc1_remotePath = None, imageSrc2_remotePath= None, imageRfr_remotePath=None):
	config_src_filename = currentUserLocalDir + 'source.txt'
	config_rfr_filename = currentUserLocalDir + 'reference.txt'

	imageEPSG = Image.objects.get(pk=1).epsg
	print "setup_configuration_files"
	print imageEPSG
	print imageSrc1_remotePath

	config_src = open(config_src_filename, 'w')
	config_src.truncate()
	line1 = imageSrc1_remotePath + "," + str(imageEPSG)
	line2 = imageSrc2_remotePath + "," + str(imageEPSG)	
	config_src.write(line1)
	config_src.write("\n")
	config_src.write(line2)
	config_src.write("\n")
	config_src.close()

	config_rfr = open(config_rfr_filename, 'w')
	config_rfr.truncate()
	line1 = imageRfr_remotePath + "," + str(imageEPSG)
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

def	remote_run_routine_and_save(currentUserName= None, hostname=None, username=None, password=None):
	print "remote_run_routine_and_save"

	UseGSSAPI = True             # enable GSS-API / SSPI authentication
	DoGSSAPIKeyExchange = True
	port = 22
	# now, connect and use paramiko Client to negotiate SSH2 across the connection
	try:
		client2 = paramiko.SSHClient()
		print('*** MODULE Connecting...')
		client2.load_system_host_keys()
		client2.set_missing_host_key_policy(paramiko.WarningPolicy())
		client2.connect(hostname, port, username, password)
		print('*** MODULE Connecting 1...')

		# channel = client2.invoke_shell()
		# stdin = channel.makefile('wb')
		# stdout = channel.makefile('rb')
		# stdin.write('''
		# cd tmp
		# ls
		# exit
		# ''')
		# print stdout.read()

		# stdout.close()
		# stdin.close()
		currentUsrRemoteHomePath = roothPath + 'users/' + currentUserName + '/'
		changeToUsrDir = 'cd ' + currentUsrRemoteHomePath
		multipleSShCommands = changeToUsrDir + '; groovy ' + groovyScript + ' source.txt ' + 'reference.txt'
		print multipleSShCommands

		# stdin, stdout, stderr = client2.exec_command(changeToUsrDir)
		stdin, stdout, stderr = client2.exec_command(multipleSShCommands)

		print('*** MODULE Connecting 2...')

		data = stdout.read().splitlines()
		for line in data:
			print line
    	
		sftp_session = client2.open_sftp()
		sftp_session.get(currentUsrRemoteHomePath + 'out/source_rgb_geo.tif', settings.MEDIA_ROOT + '/out/' + currentUserName+ '_output.tif') 
		sftp_session.close()

		client2.close()

		# outputToDB = Image(output = settings.MEDIA_ROOT + '/out/' + currentUserName+ '_output.tif')

		# outputToDB.save()

	except Exception as e:
		print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
    	traceback.print_exc()
    	try:
    		client2.close()
    	except:
        	pass
