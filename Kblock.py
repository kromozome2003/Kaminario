#!/usr/bin/python
# coding: latin-1

import krest, datetime, requests, time, curses, os

#	Use concole if the console module was downloaded and installed
#	Can be found here: http://effbot.org/zone/console-handbook.htm
#import console

#	Use subprocess if running Python 2.7 and later
#import subprocess
from datetime import datetime


class Kblock(object):
	"""
	Attributes:
		username : a string that represent the username
		password : a string that represent the user password
		ipaddr : a string that is address of the storage array (VIP)
	"""

	# Suppress the https warning
	requests.packages.urllib3.disable_warnings()

	# Store class hobjects
	vols = []
	hosts = []
	mappings = []
	volumegroups = []


	k_endpoints = [
		'host_fc_ports',
		'host_groups',
		'host_iqns',
		'hosts',
		'mappings',
		'retention_policies',
		'snapshots',
		'vg_capacity_policies',
		'volsnaps',
		'volume_groups',
		'volumes',
		'replication/sessions',
		'replication/peer_k2arrays'
	]

	k_stats_endpoints = [
		'stats/system',
		'stats/volumes'
	]

	k_max_vol_per_vg = 32

	def __init__(self, ipaddr, username='admin', password='admin'):
		"""
		Class constructor
		"""
		self.username = username
		self.password = password
		self.ipaddr = ipaddr
		print "--- Getting connected to the system... ---"
		self.endpoint = krest.EndPoint(self.ipaddr, self.username, self.password, ssl_validate=False)
		print "\tConnected to ip:%s as %s" % (self.ipaddr, self.username)

	def get_ep(self):
		"""
		return the endpoint object
		:rtype: endpoint connection
		"""
		return self.endpoint

	def set_username(self, username):
		"""
		set username in self.username
		:param: username:string
		"""
		self.username = username

	def get_username(self):
		"""
		return the username
		:rtype: username:string
		"""
		return self.username

	def set_password(self, password):
		"""
		set password in self.password
		:param: password:string
		"""
		self.password = password

	def get_password(self):
		"""
		return the password
		:rtype: password:string
		"""
		return self.password

	def lookup(self, object_type, search_pattern=''):
		"""
		lookup for objects
		:param: object_type:string, search_pattern:string
		:rtype: ResultSet
		"""
		objects = self.endpoint.search(object_type, name__contains=search_pattern)
		display_that_contains = "that contains '"+search_pattern+"'"
		if search_pattern == '':
			display_that_contains = ''
		print "Found %s %s %s" % (objects.total, object_type,display_that_contains)
		for object in objects:
			print object
		return objects

	def get_summary(self):
		print "--- Printing summary ---"
		for k_objects in self.k_endpoints:
			self.lookup(k_objects)

	def ktop(self):
		sorted_column = 0
		sorting_order = True
		screen = curses.initscr()
		screen.keypad(1)
		curses.cbreak()
		screen.nodelay(1)
		system_status = self.get_object_by_name("system/state","")
		# DISPLAY TEMPLATE
		system_state_template = "{0:>10} {1:>10} {2:>10} {3:>15} {4:>6} {5:>20} {6:>10}\n"
		system_capacity_template = "{0:>15} {1:>15} {2:>15} {3:>15} {4:>15} {5:>15}\n"
		system_template = "{0:>15} {1:>15} {2:>9} {3:>9} {4:>14} {5:>14}\n"
		replication_template = "{0:>11} {1:>12} {2:>12} {3:>13}\n"
		volumes_template = "{0:<25} {1:>15} {2:>15} {3:>9} {4:>9} {5:>14} {6:>14}\n"
		try:
			while True:
				#	Use below if running Python 2.6
				(height, width) = os.popen('stty size', 'r').read().split()
				#	Use below if console module was downloaded and installed
#				(width, height) = console.getTerminalSize()
				#	Use below if running  Python 2.7 and later instead of above
#				(height, width) = subprocess.check_output(['stty', 'size']).split()

				screen.erase()
				# HEADER
				screen.addstr("SCREEN SIZE : %s columns %s rows" % (width, height) + "\n")
				screen.addstr("CURRENT TIME : %s" % datetime.now() + "\n")
				screen.addstr("\n")
				# SYSTEM STATUS
				screen.addstr("SYSTEM STATUS\n", curses.A_REVERSE)
				screen.addstr(system_state_template.format("USER_ROLE", "API_VER.", "STATE", "CONNECTIVITY", "ID", "NAME", "VERSION"), curses.A_BOLD)
				screen.addstr(system_state_template.format(system_status.current_user_role, system_status.rest_api_version, system_status.state, system_status.system_connectivity_type, system_status.system_id, system_status.system_name, system_status.system_version))
				screen.addstr("\n")
				# SYSTEM CAPACITY
				screen.addstr("SYSTEM CAPACITY\n", curses.A_REVERSE)
				screen.addstr(system_capacity_template.format("TOTAL", "PROVISIONED", "ALLOCATED", "PHYSICAL", "REDUCTION", "REDUC.w/Thin"), curses.A_BOLD)
				system_capacity = self.get_object_by_name("system/capacity","")
				screen.addstr(system_capacity_template.format(str(system_capacity.total/1024/1024)+" GiB", str(system_capacity.provisioned/1024/1024)+" GiB", str(system_capacity.allocated/1024/1024)+" GiB", str(system_capacity.physical/1024/1024)+" GiB", str(round(float(system_capacity.allocated/system_capacity.physical),2))+":1", str(round(float(system_capacity.provisioned/system_capacity.physical),2))+":1"))
				screen.addstr(system_capacity_template.format("", str(system_capacity.provisioned*100/system_capacity.total)+" %", str(system_capacity.allocated*100/system_capacity.total)+" %", str(system_capacity.physical*100/system_capacity.total)+" %", str(int(system_capacity.allocated/system_capacity.physical*system_capacity.physical/1024/1024))+" GiB", str(int(system_capacity.provisioned/system_capacity.physical*system_capacity.physical/1024/1024))+" GiB"))
				screen.addstr("\n")
				# SYSTEM STATS
				screen.addstr("SYSTEM STATS\n", curses.A_REVERSE)
				screen.addstr(system_template.format("THROUGHPUT_AVG", "THROUGHPUT_MAX", "IOPS_AVG", "IOPS_MAX", "LATENCY_OUTER", "LATENCY_INNER"), curses.A_BOLD)
				system = self.get_object_by_name("stats/system","")
				screen.addstr(system_template.format(str(system.throughput_avg/1024/1024)+" MB/s", str(system.throughput_max/1024/1024)+" MB/s", system.iops_avg, system.iops_max, str(system.latency_outer)+" msec", str(system.latency_inner)+" msec"))
				screen.addstr("\n")
				# REPLICATION STATS
				screen.addstr("REPLICATION STATS\n", curses.A_REVERSE)
				screen.addstr(replication_template.format("LOGICAL_IN", "LOGICAL_OUT", "PHYSICAL_IN", "PHYSICAL_OUT"), curses.A_BOLD)
				replication = self.get_object_by_name("replication/stats/system","")
				screen.addstr(replication_template.format(str(replication.logical_in/1024/1024)+" MB/s", str(replication.logical_out/1024/1024)+" MB/s", str(replication.physical_in/1024/1024)+" MB/s", str(replication.physical_out/1024/1024)+" MB/s"))
				screen.addstr("\n")
				# VOLUMES STATS
				screen.addstr("VOLUMES STATS\n", curses.A_REVERSE)
				screen.addstr(volumes_template.format("(0)", "(1)", "(2)", "(3)", "(4)", "(5)", "(6)"), curses.A_UNDERLINE)
				screen.addstr(volumes_template.format("NAME", "THROUGHPUT_AVG", "THROUGHPUT_MAX", "IOPS_AVG", "IOPS_MAX", "LATENCY_OUTER", "LATENCY_INNER"), curses.A_BOLD)
				volumes = self.endpoint.search("stats/volumes", volume_name="").hits
				vol_count = len(volumes)
				index=0
				vols = []
				while index < vol_count:
					vol = (volumes[index].volume_name, volumes[index].throughput_avg, volumes[index].throughput_max, volumes[index].iops_avg, volumes[index].iops_max, volumes[index].latency_outer, volumes[index].latency_inner)
					#if index <= (height-25):
					vols.append(vol)
					index += 1
				sorted_vols = sorted(vols, key=lambda v : v[sorted_column], reverse=sorting_order)
				index=0
				vols = []
				for voltodisplay in sorted_vols:
					if index <= (int(height)-25):
						vols.append(voltodisplay)
						index += 1
				for volume in vols:
					screen.addstr(volumes_template.format(volume[0], str(volume[1]/1024/1024) + " MB/s", str(volume[2]/1024/1024) + " MB/s", volume[3], volume[4], volume[5], volume[6]))
				screen.refresh()
				time.sleep(1)

				# LISTENER
				c = screen.getch()
				if c == ord('0'):
					sorted_column = 0
				if c == ord('1'):
					sorted_column = 1
				if c == ord('2'):
					sorted_column = 2
				if c == ord('3'):
					sorted_column = 3
				if c == ord('4'):
					sorted_column = 4
				if c == ord('5'):
					sorted_column = 5
				if c == ord('6'):
					sorted_column = 6
				if c == ord('r'):
					sorting_order = not sorting_order
				if c == ord('q'):
					exit(0)
		finally:
			curses.endwin()

	def get_object_by_name(self, object_type, search_pattern, verbose=False):
		"""
		find one single objects by name
		:param object_type:
		:param search_pattern:
		:return: found object
		:rtype: Object
		"""
		if verbose:
			print "--- Checking if '%s' exists in %s ---" % (search_pattern, object_type)
		objects = self.endpoint.search(object_type, name=search_pattern)
		if objects.total>0:
			if verbose:
				print "\t%s %s exists !" % (object_type, search_pattern)
			return objects.next()
		else:
			if verbose:
				print "\tNot found"
			return None


	def create_vg(self, vgname, quota, is_dedup):
		"""
		:param vgname:
		:param quota:int in GB
		:return:
		:rtype: vg
		"""
		if quota == 0:
			quota_message="unlimited"
		else:
			quota_message=str(quota)+"GB"
		if is_dedup:
			dedup_message="ON"
		else:
			dedup_message="OFF"

		print "--- Creating VG:%s with %s quota and dedup:%s ---" % (vgname,quota_message,dedup_message)
		vg = self.get_object_by_name("volume_groups",vgname)
		if vg is None:
			vg = self.endpoint.new("volume_groups", name=vgname, quota=quota*1024*1024, is_dedup=is_dedup)
			if quota>0:
				vg.capacity_policy = self.endpoint.search("vg_capacity_policies").hits[0]  # search ad-hoc
			vg.save()
			print "--- VG:%s Created ---" % vgname
			self.volumegroups.append(vg)
		return vg

	def get_vg_vol_count(self, vgname):
		"""
		:param vgname:
		:return:
		:rtype: vg
		"""
		vg = self.get_object_by_name("volume_groups",vgname)
		if vg is None:
			return 32
		else:
			vols = self.endpoint.search("volumes", volume_group=vg)
			return vols.total

	def delete_vg(self, vgname, force=False):
		"""
		:param vgname:
		:param quota:int in GB
		:return:
		:rtype: None
		"""
		print "--- Deleting VG:%s" % vgname
		vg = self.get_object_by_name("volume_groups",vgname)
		if vg is not None:
			vols = self.endpoint.search("volumes", volume_group=vg)
			if vols.total>0:
				print "\tThere are %s vols to delete first!" % vols.total
				for vol in vols:
					self.delete_vol(vol.name)
		vg.delete()
		print "\tVG:%s Deleted ---" % vgname

	def create_vols(self, vgname_prefix, qty=1, size=1, prefix='vol_', vg_quota=0, vmware_support=False, is_dedup=False, mapto=None, hosttype=None):
		"""
		create volumes
		:param vgname:
		:param qty:
		:param size: 
		:param prefix:
		"""
		voli = 0
		vgi = 0
		vgname = vgname_prefix
		print "--- Creating %s vols of %GB in VG:%s with prefix:%s ---" % (qty,size,vgname,prefix)
		vg = self.get_object_by_name("volume_groups",vgname)
		if vg is None:
			vg = self.create_vg(vgname,vg_quota,is_dedup)
		while voli < qty:
			if self.get_vg_vol_count(vgname) == self.k_max_vol_per_vg:
				vgi += 1
				vgname = vgname_prefix+"_"+str(vgi)
				vg = self.create_vg(vgname,vg_quota,is_dedup)
			volname = prefix+str(voli)

			vol = self.get_object_by_name("volumes",volname)
			if vol is None:
				vol = self.create_vol(volname, size, vgname, vmware_support)
				if mapto is not None and hosttype is not None:
					host = self.create_host(mapto,hosttype)
					mapping = self.endpoint.new("mappings", volume=vol, host=host).save()
					print "\tVOL:%s mapped to HOST:%s" % (volname,host.name)
					self.mappings.append(mapping)
				voli += 1
			else:
				print "\t%s already exists, tryng the next one" % volname
				voli += 1
				qty += 1
		return voli

	def list_created_vols(self):
		for vol in self.vols:
			print "\t%s" % vol.name

	def list_created_hosts(self):
		for host in self.hosts:
			print "\t%s" % host.name

	def list_created_vgs(self):
		for vg in self.volumegroups:
			print "\t%s" % vg.name

	def create_vol(self, volname, size, vgname, vmware_support=False):
		vg = self.get_object_by_name("volume_groups",vgname)
		if vg is None:
			vg = self.create_vg(vgname)
		vol = self.endpoint.new("volumes", name=volname, size=size*1024*1024, volume_group=vg, vmware_support=vmware_support)
		vol.save()
		print "\t%s (%s GB) created in VG %s with vmware_support:%s" % (volname,size,vg.name,vmware_support)
		self.vols.append(vol)
		return vol

	def replicate_vg(self, session_name, local_vg, peer_k2sid, auto_configure_peer_volumes=True, rpo=60):
		session = self.get_object_by_name("replication/sessions",session_name)
		peer_k2array_object = self.get_object_by_name("replication/peer_k2arrays",peer_k2sid)
		local_volume_group = self.get_object_by_name("volume_groups",local_vg)
		if session is None:
			session = self.endpoint.new("replication/sessions", replication_peer_k2array=peer_k2array_object, auto_configure_peer_volumes=auto_configure_peer_volumes, local_volume_group=local_volume_group, name=session_name, rpo=rpo)
			session.save()
			print "\tSESSION %s has been created" % session_name
			session.state='in_sync'
			session.save()
			print "\tSESSION %s is in sync" % session_name
		else:
			print "\tSESSION %s already exists" % session_name
		return session

	def create_host(self, hostname, hosttype='Linux'):
		host = self.get_object_by_name("hosts",hostname)
		if host is None:
			host = self.endpoint.new("hosts", name=hostname, type=hosttype).save()
			print "\tHost %s (type:%s) created" % (hostname,hosttype)
			self.hosts.append(host)
		else:
			print "\tHost %s already exists" % hostname
		return host

	def set_host_pwwn(self, hostname, pwwn):
		host = self.get_object_by_name("hosts",hostname)
		if host is not None:
			host_fc_port = self.endpoint.new("host_fc_ports", host=host, pwwn=pwwn).save()
			print "\tPWWN %s associated to host %s" % (pwwn,hostname)
		else:
			print "\tHost %s already exists" % hostname
		return host_fc_port

	def set_host_iqn(self, hostname, iqn):
		host = self.get_object_by_name("hosts",hostname)
		if host is not None:
			host_iqn = self.endpoint.new("host_iqns", host=host, iqn=iqn).save()
			print "\tIQN %s associated to host %s" % (iqn,hostname)
		else:
			print "\tHost %s already exists" % hostname
		return host_iqn

	def delete_host(self, hostname):
		"""
		delete host
		"""
		print "--- Deleting HOST:%s" % hostname
		host = self.get_object_by_name("hosts",hostname)
		if host is not None:
			mappings = self.endpoint.search("mappings", host=host)
			if mappings.total>0:
				print "\tThere are %s mappings to delete" % mappings.total
				for mapping in mappings:
					mapping.delete()
			host.delete()
			print "\tHOST:%s Deleted" % hostname

	def delete_mapping(self, volname):
		"""
		delete mapping
		"""
		print "--- Deleting mapping to VOL:%s" % volname
		vol = self.get_object_by_name("volumes",volname)
		mappings = self.endpoint.search("mappings", volume=vol)
		if mappings.total>0:
			print "\tThere are %s mappings to delete" % mappings.total
			for mapping in mappings:
				mapping.delete()
		print "\tMapping for VOL:%s Deleted" % volname

	def delete_vol(self, volname):
		"""
		delete volumes
		"""
		print "--- Deleting VOL:%s" % volname
		vol = self.get_object_by_name("volumes",volname)
		if vol is not None:
			self.delete_mapping(volname)
			vol.delete()
			print "\tVOL:%s Deleted" % volname


	def delete_created_vols(self):
		for vol in self.vols:
			self.delete_vol(vol.name)

	def delete_created_vgs(self):
		for vg in self.volumegroups:
			self.delete_vg(vg.name)

	def delete_created_hosts(self):
		for host in self.hosts:
			self.delete_host(host.name)

