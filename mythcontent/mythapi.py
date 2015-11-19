import urllib.request
import json
import xmltodict
import iso8601
from collections import namedtuple
storage_group = namedtuple('StorageDir', ['host','name','directory'])



tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'description', 'start_at', 'length', 'channel_number', 'host',
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
		self.tv_programs = None # This is more expensive, so don't set this until and unless it's needed.

	"""
	Make a call to the MythTV API and request XML back from MythTV server.
	Pass:
	  * name of API service
	  * name of API call within service
	  * data (optional)
	  * headers (optional)
	Returns:
	  * An ordereddict created by parsing the XML returned from the MythTV server
	"""
	def _call_myth_api_for_xml(self,service_name, call_name, data=None, headers=None):
		# urlopen doesn't always work if headers is None:
		if headers is None:
			headers = {}
		# Does headers contain 'Accept'?
		if 'Accept' in headers:
			# If headers['Accept'] is requesting JSON, delete that key.
			if headers['Accept'] == 'text/javascript' or headers['Accept'] == 'application/json':
				del headers['Accept']
		# Assemble url:
		url = (
			"http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, call_name)
			)
		# Make a Request object and pass it to the server.
		# Use the returned result to make some XML to return to our caller
		req = urllib.request.Request(url, data, headers)
		with urllib.request.urlopen(req) as response:
			the_answer = response.read()
			return xmltodict.parse(the_answer)
		

	"""
	Gets list of storage groups available to
	MythTV server self.server_name.
	 Pass: self
	 Return: list, each element of which is
	 a (host, name, directory) namedtuple.
	 On failure, or if there are no storage groups, returns empty list.
	"""
	def _discover_storage_groups(self):
		sgxml = self._call_myth_api_for_xml('Myth', 'GetStorageGroupDirs')
		sgdirs = sgxml['StorageGroupDirList']['StorageGroupDirs']['StorageGroupDir']
		retlist = []
		for sg in sgdirs:
			retlist.append(storage_group(sg['HostName'],sg['GroupName'],sg['DirName']))
		return retlist


	"""
	Pass:
	 * storage group name
	 * host (optional)
	 (If no host is given, assume self.server_name.)
	Return:
	 * the corresponding directory, or None if no match
	"""
	def get_storage_dir(self, name='', host=None):
		if host is None:
			host = self.server_name
		for sg in self.storage_groups:
			if sg.host == host and sg.name == name:
# 			if sg[0] == host and sg[1] == name:
				return sg.directory
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
		progdict = self._call_myth_api_for_xml('Dvr', 'GetRecordedList')
		proglist = progdict['ProgramList']['Programs']['Program']
		retlist = []
# 		tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'start_at', 'length', 'channel_number', 'host',
# 	'storage_group', 'file_name', 'file_size' ])
		for p in proglist:
			# Get duration:
			start_dt = iso8601.parse_date(p['Recording']['StartTs'])
			end_dt = iso8601.parse_date(p['Recording']['EndTs'])
			prog_dur = end_dt - start_dt
			seconds = prog_dur.seconds
			days, seconds = divmod(seconds, 86400)
			hours, seconds = divmod(seconds, 3600)
			minutes, seconds = divmod(seconds, 60)
# 			dstr = "{} days, {} hours, {} minutes".format(days, hours, minutes)
# 			
			if days > 0:
				dstr = '%d day' % (days)
				if days > 1:
					dstr = dstr + 's'
				dstr = dstr + ' '
			else:
				dstr = ''
			dstr = dstr + '%dh %02dm' % (hours, minutes)
			retlist.append( tv_recording(p['Title'], p['SubTitle'], p['Description'], p['Recording']['StartTs'], dstr, p['Channel']['ChanNum'], p['HostName'],
							p['Recording']['StorageGroup'], p['FileName'], p['FileSize'] ) )
# 			retlist.append(t)
		return retlist
		
		
		
			

	
