import urllib.request
import json
from collections import namedtuple
storage_group = namedtuple('StorageDir', ['host','name','directory'])



tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'start_at', 'length', 'channel_id', 'host',
	'storage_group', 'file_name', 'file_size' ])


class MythApi(object):
	"""
	This class encapsulates the code to interact with a
	MythTV server via its API.
	"""
	def __init__(self, server_name = 'mythbackend1', port=6544):
		self.server_name = server_name
		self.server_port = port
		self.storage_groups = self._discover_storage_groups()
		self.video_storage_group = self.get_storage_dir(name='Videos')
		self.default_storage_group = self.get_storage_dir(name='Default')
		self.tv_programs = None # Don't set this until it's needed.

	"""
	Gets list of storage groups available to
	MythTV server self.server_name.
	 Pass: self
	 Return: list, each element of which is
	 a (host, name, directory) namedtuple.
	 On failure, or if there are no storage groups, returns empty list.
	"""
	def _discover_storage_groups(self):
		retlist = []
		service_name='Myth'
		api_call='GetStorageGroupDirs'
		url = (
			"http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, api_call)
			)
		data = None
		headers = { 'Accept':'application/json' }
		req = urllib.request.Request(url, data, headers)
		with urllib.request.urlopen(req) as response:
			the_answer = response.read()
			sgjson = json.loads(the_answer.decode('utf-8'))
		sgdirs = sgjson['StorageGroupDirList']['StorageGroupDirs']
		for sg in sgdirs:
			retlist.append(storage_group(sg['HostName'],sg['GroupName'],sg['DirName']))
		return retlist

	"""
	Pass: storage group name and host.
	Return: the corresponding directory.
	If no host is given, assume self.server_name.
	If no match, return None
	"""
	def get_storage_dir(self, name='', host=None):
		if host is None:
			host = self.server_name
		for sg in self.storage_groups:
			if sg[0] == host and sg[1] == name:
				return sg[2]
		return None

	"""
	Calls the Myth server and gets a list
	of recorded TV programs. Does not return
	all the info returned by the API call, only
	that which we'll need:
	'title', 'subtitle', 'start_at', 'length', 'channel_id', 'host',
	'storage_group', 'file_name', 'file_size'
	Pass: self
	Return: list, each element of which is a named
	tuple with above members
	If api call fails, return None.
	If program list is empty, return []
	"""
	def discover_tv_programs(self):
		service_name='Dvr'
		api_call='GetRecordedList'
		url = (
			"http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, api_call)
			)
		data = None
		headers = { 'Accept':'application/json' }
		req = urllib.request.Request(url, data, headers)
		with urllib.request.urlopen(req) as response:
			the_answer = response.read()
			sgjson = json.loads(the_answer.decode('utf-8'))
		proglist = sgjson['Programs']['ProgramList']
		
		
			

	
