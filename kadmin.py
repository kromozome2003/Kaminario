#!/usr/bin/env python

import csv, time, argparse
from Kblock import Kblock

# PREREQUISITES
#	Install Python 2.7
#	sudo easy_install pip	// Install pip for MAC OSX
#	sudo pip install krest	// Install the krest python lib

# initiate a connection
#mykblock = Kblock('10.0.23.100', 'admin', 'areas00')
#mykblock = Kblock('192.168.7.10', 'admin', 'Kaminario1')

#  Change the copany name then
company='client'
#  Separator for naming convention ie. <company>[SEPARATOR]<hostname>[SEPARATOR]<vgname>[SEPARATOR]<volname>
separator='-'

###
#  Read volume mapping from csv
def parse_csv(mappingfile):
    with open(mappingfile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if (str(row[0]).startswith('#') is False) :

                # KBLOCK
                if str(row[0])=='KBLOCK':
                    fqdn=row[1]
                    username=row[2]
                    password=row[3]
                    print "- CONNECTING to %s with username %s" % (fqdn,username)
                    mykblock = Kblock(fqdn, username, password)

                # TEMPO
                if str(row[0])=='TEMPO':
                    seconds=float(row[1])
                    print "- TEMPO for %f seconds" % (seconds)
                    time.sleep(seconds)

                # CREATE-VOLUMES
                if str(row[0])=='CREATE-VOLUMES':
                    volume_name=row[1]
                    vmware_support=row[2]
                    is_dedup=row[3]
                    volcount=float(row[4])
                    volsize=float(row[5])
                    vgname = volume_name+separator+'VG'
                    volname = volume_name+separator+'VOL'
                    print "- CREATE-VOLUMES"
                    mykblock.create_vols(vgname,volcount,volsize,volname,vmware_support=vmware_support,is_dedup=is_dedup)

                # CREATE-AND-MAP
                if str(row[0])=='CREATE-AND-MAP':
                    hostname=row[1]
                    hosttype=row[2]
                    vmware_support=row[3]
                    is_dedup=row[4]
                    volcount=float(row[5])
                    volsize=float(row[6])
                    volsuffix=''
                    if len(row)>7:
                        volsuffix=row[7]
                    vgname = hostname+separator+'vg'
                    volname = hostname+separator+'vol'
                    print "- CREATE-AND-MAP for host:%s" % (hostname)
                    mykblock.create_vols(vgname,volcount,volsize,volname+separator+volsuffix,vmware_support=vmware_support,is_dedup=is_dedup,mapto=hostname,hosttype=hosttype)

                # CREATE-SERVER
                if str(row[0])=='CREATE-SERVER':
                    hostname=row[1]
                    hosttype=row[2]
                    print "- CREATE-SERVER for host:%s with OS:%s" % (hostname,hosttype)
                    mykblock.create_host(hostname,hosttype)

                # MAP-PWWN
                if str(row[0])=='MAP-PWWN':
                    hostname=row[1]
                    pwwn=row[2]
                    print "- MAP-PWWN for host:%s with PWWN:%s" % (hostname,pwwn)
                    mykblock.set_host_pwwn(hostname,pwwn)

                # MAP-IQN
                if str(row[0])=='MAP-IQN':
                    hostname=row[1]
                    iqn=row[2]
                    print "- MAP-IQN for host:%s with IQN:%s" % (hostname,iqn)
                    mykblock.set_host_iqn(hostname,iqn)

                # CLEANUP
                if str(row[0])=='CLEANUP':
                    print "- CLEANUP created objects"
                    mykblock.delete_created_vols()
                    mykblock.delete_created_vgs()
                    mykblock.delete_created_hosts()




###
#  Create 5 ESX Hosts with 10 vols of 100GB mapped on each (WITH DEDUP)
#index=1
#while index <= 11:
#    index_str=str(index)
#    hostname = 'CPAR02'
#    #vgname = hostname+separator+'vg'
#    vgname = hostname+separator+'vg'
#    volname = 'K'+separator+'PVS'+separator+'vol'
#    #print "%d - Creating host %s" % (index,hostname)
#    print "%d - Creating vols %s" % (index,hostname)
#    mykblock.create_vols(vgname,1,250,volname,vmware_support=False,is_dedup=True)
#    index += 1
###

###
#  Create 5 Linux/Oracle Hosts with 10 vols mapped on each (WITHOUT DEDUP)
#       2 x 5GB for REDO + 2 x 10GB for ARCH + 1 x 30GB for BINARIES + 1 x 100GB for DUMP + 4 x 100GB for DATA
#index=1
#while index <= 3:
#    index_str=str(index)
#    hostname = company+separator+'ORAhost'+index_str
#    vgname = hostname+separator+'vg'
#    volname = hostname+separator+'vol'
#    print "%d - Creating host %s" % (index,hostname)
#    mykblock.create_vols(vgname,2,5,volname+'REDO',vmware_support=False,is_dedup=False,mapto=hostname,hosttype='Linux')
#    mykblock.create_vols(vgname,2,10,volname+'ARCH',vmware_support=False,is_dedup=False,mapto=hostname,hosttype='Linux')
#    mykblock.create_vols(vgname,1,30,volname+'BIN',vmware_support=False,is_dedup=False,mapto=hostname,hosttype='Linux')
#    mykblock.create_vols(vgname,1,100,volname+'DUMP',vmware_support=False,is_dedup=False,mapto=hostname,hosttype='Linux')
#    mykblock.create_vols(vgname,4,100,volname+'DATA',vmware_support=False,is_dedup=False,mapto=hostname,hosttype='Linux')
#    index += 1
###

######  HELP  ########


# print storage array objects count
#mykblock.get_summary()

# print storage array objects count
#mykblock.ktop()

# find how many objects contains 'mike' in it's name
#mykblock.lookup('volume_groups','mike')

# find how many objects contains 'mike' in it's name
#mykblock.lookup('volumes','mike')

# loop for vg by name
#vg = mykblock.get_object_by_name('volume_groups','mike3')

# delete it
#vg.delete()

# create VG without quota (GB)
#mykblock.create_vg('mikevg',0)

# create 10 vols of 100GB in VG 'vgtestmike'
	# automatically add vgtestmike_X if exceed the VG limit
	# create the vg if it doesn't exists
	# default volume size = 1GB
	# vmware_support True / False(default)
#mykblock.create_vols('vgtestmike',2,100,'volvgmike_',vmware_support=False,is_dedup=True)
#mykblock.create_vols('vgtestmike',2,100,'volvgmike_',vmware_support=False,is_dedup=True,mapto='mikehost',hosttype='Linux')

# Wait 1 minute
#time.sleep(20)

# Delete all created (by this script) vols. Previously created objects stay in config
#mykblock.delete_created_vols()

# Delete all created (by this script) vg. Previously created objects stay in config
#mykblock.delete_created_vgs()

# Delete all created (by this script) hosts. Previously created objects stay in config
#mykblock.delete_created_hosts()

# delete host and mapping as well
#mykblock.list_created_vols()

# Delete specific host
#mykblock.delete_host('FranceHost1')

# delete vg, volumes and mapping as well
#mykblock.delete_vg('CPAR02-PVS-vg')

# Create host
#mykblock.create_host('mikehost','Linux')

parser = argparse.ArgumentParser(description='Admin tool for K2')
parser.add_argument('-a','--action', help='Action to run : ktop | parse', required=True)
file_group = parser.add_argument_group(title='PARSE', description='Read csv file to process admin tasks.')
file_group.add_argument('-f', "--filename", help='The path to the csv file.')
ktop_group = parser.add_argument_group(title='KTOP', description='Unix like TOP screen to monitor K2 system.')
ktop_group.add_argument('-H','--hostname', help='ip/fqdn of K2 system')
ktop_group.add_argument('-u','--username', help='user')
ktop_group.add_argument('-p','--password', help='password')
args = parser.parse_args()
if (args.action == 'parse' and args.filename):
    parse_csv(args.filename)
elif (args.action == 'ktop' and args.hostname and args.username and args.password):
    mykblock = Kblock(args.hostname, args.username, args.password)
    mykblock.ktop()