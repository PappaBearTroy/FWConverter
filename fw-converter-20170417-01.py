print("Please Create a directory at c:\\convert	")
print("Please place ASA config in said directory")
print("WITH THE NAME (make a copy etc) of asa.config")
print(" ")
print(" ")
print(" ")

import os
## open files for reading/writing
original_file = open('c:\\convert\\asa.config', 'r')
## lots of dup addresseseseses possible; so create temp file, then remove dupes
new_temp_address_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-ADD-objects-withdups.txt', 'w')

new_address_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-ADD-objects.txt', 'w')
new_address_group_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-ADD-Groups-objects.txt', 'w')
new_service_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-SVC-objects.txt', 'w')
new_service_group_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-SVC-Groups-objects.txt', 'w')
new_nat_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-NAT-objects.txt', 'w')
new_fw_policies_file = open('c:\\convert\\ASA-to-Fortinet-converted-FW-policies.txt', 'w')

#need to convert Cisco built in service objects to actual ports or names used by other vendors
cisco_protocol_list = ["aol", "5120", "bgp", "179", "chargen", "19", "cifs", "3020", "citrix-ica", "1494", "cmd", "514", "ctiqbe", "2748", "daytime", "13", "discard", "9", "domain", "53", "echo", "7", "exec", "512", "finger", "79", "ftp", "21", "ftp-data", "20", "gopher", "70", "h323", "1720", "hostname", "101", "http", "80", "https", "443", "ident", "113", "imap4", "143", "irc", "194", "kerberos", "88", "klogin", "543", "kshell", "544", "ldap", "389", "ldaps", "636", "login", "513", "lotusnotes", "1352", "lpd", "515", "netbios-ssn", "139", "nfs", "2049", "nntp", "119", "pcanywhere-data", "5631", "pim-auto-rp", "496", "pop", "2109", "pop", "3110", "pptp", "1723", "rsh", "514", "rtsp", "554", "sip", "5060", "smtp", "25", "sqlnet", "1522", "ssh", "22", "sunrpc", "111", "tacacs", "49", "talk", "517", "telnet", "23", "uucp", "540", "whois", "43", "www", "80"]

print("Starting Firewall Conversion")
print("Current version is 2017.0417")
print(" ")
print("Written and coded by TroyC, ")
print("	debuged using either Modern Times Orderville")
print("	or when things got out of hand, Bottle Logic Stable Orbit")
print(" ")
print("This is a rudementary parser/converter;")
print("Currently it only takes a Cisco ASA config file as input")
print("with the only output (in multiple files) for a Fortinet config.")
print(" ")
print("Future versions may provide input/output for Junos and Palo Alto")
print("and possibly a full input/output matrix.")
print("	Currently worried there's not enough beer for that.")
print("	")
print("It is important to note -- ")
print("	Not all portions of the configuration are dealt with.")
print("	")
print("Aspects such as VPNs require pre-shared keys and interface mapping")
print("	")
print("This parser was created simply to ease the major conversion tasks")
print("such as objects (both network and service)")
print("as well as the ACLs to FW rules.")
print("	")
print("	")
print("Here are some of the items Converted or Not converted")
print("	")
print("	")
### what a mess to get the tabs correct to get columns lined up
print("	Converted			Not Converted            ")
print("------------------------------------------------------")
print("	object network			name")
print("	object-group network		dhcp")
print("	object service			dns")
print("	object-group service		interface naming")
print("	ACLs				interface IP address")
print("					Security Zones (N/A in ASA)")
print("	object network NAT		old NAT & No-NAT statements")
print("					rip/ospf")
print("					static routes")
print("					crypto/vpn")
print("	")


def create_fw_policy_fortinet(srcaddr, dstaddr, action, service, is_enabled, rule_number, comment):
	
	## take conversions and format for Fortinet
	#rule_number = "edit " + str(acl_counter)
	srcintf = "set srcintf \"any\" "
	dstintf = "set dstintf \"any\" "
	service = service.upper()
	
	## write new policies out
	new_fw_policies_file.write(rule_number+ txt_eol)
	new_fw_policies_file.write(srcintf + txt_eol + dstintf + txt_eol)
	new_fw_policies_file.write("set srcaddr \"" + srcaddr + "\"" + txt_eol + "set dstaddr \"" + dstaddr + txt_eol)
	new_fw_policies_file.write("set action " + action + txt_eol + "set schedule \"always\"" + txt_eol)
	new_fw_policies_file.write("set service \"" + service + "\"" + txt_eol + "set nat enable" + txt_eol) 
	new_fw_policies_file.write("set comments \"" + comment + txt_eol + "next" + txt_eol)
	pass
	
def create_net_address(obj_name,ip_add, subnet):
	## print ("In Convert Network HOST Object Function")
	if subnet == "":
		subnet = "255.255.255.255"
	## Convert & write object name
	#new_temp_address_objects_file.write(txt_edit + obj_name + txt_eol)
	#new_temp_address_objects_file.write(txt_set_sub + ip_add + " " + subnet + txt_eol + txt_next)
	new_temp_address_objects_file.write(obj_name + " " + ip_add + " " + subnet + txt_eol)
	
def create_net_nat(obj_name, priv_ip, vip):
	## print ("In Convert NAT Object Function")
	## !not done!
	new_nat_objects_file.write("edit \"VIP-" + obj_name + txt_eol)
	new_nat_objects_file.write("set extip " + vip + txt_eol + "set extintf \"any\"" + txt_eol)
	new_nat_objects_file.write("set mappedip \"" + priv_ip + "\"" + txt_eol + txt_next + txt_eol)
		
def object_convert_type_service(svc_name, svc_proto, svc_ports):
	## print ("In Convert Service Object Function")
	txt_edit 	= "edit "
	txt_set_tcp = "set tcp-portrange "	
	txt_set_udp = "set udp-portrange "	

	## See if it's tcp/udp then complete conversion
	## If it's tcp-udp then create both
	if svc_proto == "tcp":
		new_service_objects_file.write(txt_edit + svc_name + "-" + svc_proto + svc_ports + txt_eol)
		new_service_objects_file.write(txt_set_tcp + " " + svc_ports + txt_eol + txt_next)
	elif svc_proto == "udp":
		new_service_objects_file.write(txt_edit + svc_name + "-" + svc_proto + svc_ports + txt_eol)
		new_service_objects_file.write(txt_set_udp + " " + svc_ports + txt_eol + txt_next)
	elif svc_proto == "tcp-udp":
		new_service_objects_file.write(txt_edit + svc_name + "-" + "tcp" + svc_ports + txt_eol)
		new_service_objects_file.write(txt_set_tcp + " " + svc_ports + txt_eol + txt_next)
		new_service_objects_file.write(txt_edit + svc_name + "-" + "udp" + svc_ports + txt_eol)
		new_service_objects_file.write(txt_set_udp + " " + svc_ports + txt_eol + txt_next)
	## not sure a return is required
	else: return


## some definitions 
original_lines = original_file.readlines()
txt_edit 	= "edit "
txt_set_sub = "set subnet "	
txt_set_tcp = "set tcp-portrange "	
txt_set_udp = "set udp-portrange "	
txt_set		= "set"
txt_eol 	= "\n"
txt_next	= "next \n"
output_vendor = "fortinet"
# 201 just seemed like an easy number to start with
acl_counter 	= 201 

## Write initial config statements 
#new_address_objects_file.write("conf firewal address" + txt_eol)
new_service_objects_file.write("conf firewal service custom")
new_address_group_objects_file.write("conf firewal addgrp" + txt_eol)	
new_service_group_objects_file.write("conf firewal service group" + txt_eol)
new_nat_objects_file.write("config firewall vip" + txt_eol)
new_fw_policies_file.write("config firewall policy" + txt_eol)	
	
### This is where the main program lives
for counter in range(len(original_lines)):
	## split current line into individual word list
	current_line = original_lines[counter].split()

## Single Network Object // could also be a NAT statement
	if ((current_line[0] == "object") and (current_line[1] == "network")):
		## Get the next line
		line_next = original_lines[counter+1].split()
		
		## If it's a description go to next line
		if line_next[0] == "description":
			line_next = original_lines[counter+2].split()
		
		## If it's a HOST
		if (line_next[0] == "host"):
			## Create the object
			## create_net_address(obj_name,ip_add, subnet)
			create_net_address(current_line[2],line_next[1], "")
		
		## If it's a NETWORK
		elif (line_next[0] == "subnet"):
			## Create the object
			## create_net_address(obj_name,ip_add, subnet)
			create_net_address(current_line[2],line_next[1], line_next[2])
		
		## If it's a STATIC NAT
		elif (line_next[0] == "nat") and (line_next[2] == "static"):
			orig_obj_ip = ""
			
			## we only know object name and public IP
			## need to find original object definition
			for new_counter in range(len(original_lines)):
				
				## split current line into individual word list
				looking_again = original_lines[new_counter].split()
				

				if current_line[2] in looking_again:

					orig_obj_def = original_lines[new_counter+1].split()
					orig_obj_ip = orig_obj_def[1]
					break
				new_counter += 1
			
			## Create the VIP object
			## create_net_nat(obj_name, priv_ip, nat_ip)
			create_net_nat(current_line[2], orig_obj_ip, line_next[3])
			
## Single Service Object
	elif ((current_line[0] == "object") and (current_line[1] == "service")):
		## Get the next line
		line_next = original_lines[counter+1].split()
		
		## If it's a description go to next line
		if line_next[0] == "description":
			line_next = original_lines[counter+2].split()
		
		## Haven't seen it, but I guess it could be service-object or IP or something other than udp/tcp/udp-tcp
		if (line_next[1] == "tcp") or (line_next[1] == "udp") or (line_next[1] == "tcp-udp"):
			## Find destination offset
			try:
				destination_offset = line_next.index('destination')
			except:	
				destination_offset = 0

			##Is it a range or single port
			if "range" in line_next: 
				object_ports = line_next[destination_offset + 2] + "-" + line_next[destination_offset + 3]
			else:
				object_ports = line_next[destination_offset + 2]

			## Create the object
			object_convert_type_service(current_line[2], line_next[1], object_ports)

## Group Network Object
	elif ((current_line[0] == "object-group") and (current_line[1] == "network")):
		## next line incrementer
		grp_counter = 1
		
		## Get the next line
		line_next = original_lines[counter+grp_counter].split()
		
		## Initialize group member
		grp_name = "edit \"" + current_line[2] + "\""
		grp_members = "set member "
		
		
		while ((line_next[0] == "description") or (line_next[0] == "network-object")):

			## Take action if it's a n-o
			if line_next[0] == "network-object":
				
				## if it's a host, need to create object
				if (line_next[1] == "host"):
					## Create the object
					## create_net_address(obj_name,ip_add, subnet)
					create_net_address(line_next[2],line_next[2], "")
					## and then add member to group membership
					grp_members = grp_members + "\"" + line_next[2] + "\" "
				
				## if it's an object, just add to group
				elif (line_next[1] == "object"):
					## Add object to group membership
					grp_members = grp_members + "\"" + line_next[2] + "\" "
				
				## it's an IP adder; need to create object
				else:
					## Create the object
					## create_net_address(obj_name,ip_add, subnet)
					create_net_address(line_next[1],line_next[1], line_next[2])
					## and then add member to group membership
					grp_members = grp_members + "\"" + line_next[1] + " "
			
			## get next line	
			grp_counter +=1
			line_next = original_lines[counter+grp_counter].split()
		
		## Create new svcGRP and the members
		new_address_group_objects_file.write(grp_name + txt_eol)
		new_address_group_objects_file.write(grp_members + txt_eol + "next" + txt_eol)
			
## Group Service Object	
	elif ((current_line[0] == "object-group") and (current_line[1] == "service")):
		## next line incrementer
		grp_counter = 1
		
		## Get the next line
		line_next = original_lines[counter+grp_counter].split()
		
		## Initialize group member
		grp_name = "edit \"" + current_line[2] + "\""
		grp_members = "set member "
		
		## While next line is either description or s-o, or p-o; 
		## need to find a better way
		while ((line_next[0] == "description") or (line_next[0] == "service-object") or (line_next[0] == "port-object")):

			## proccess the s-o
			if (line_next[0] == "service-object"):

				## get settings for individual object
				if (line_next[1] == "tcp") or (line_next[1] == "udp") or (line_next[1] == "tcp-udp"):

					## Find destination offset
					try:
						destination_offset = line_next.index('destination')
					except:	
						destination_offset = 0

					## It is a destination range 
					if "range" in line_next[destination_offset+1]: 
						object_ports = line_next[destination_offset + 2] + "-" + line_next[destination_offset + 3]
					
					## It is an equals "eq"; however it could be a built-in service name or a port number
					else:
						## Let's take care of port numbers first
						if line_next[destination_offset + 2].isdigit():
							object_ports = line_next[destination_offset + 2]
						else:
							## Otherwise it's a common name http/https/etc)
							try:
								in_cisco_list = cisco_protocol_list.index(line_next[destination_offset+2])
							except ValueError:
								pass
							## convert it to the protocol port number, not common name
							object_ports = cisco_protocol_list[in_cisco_list +1]
					
				## add new object as group member
				## not pretty but correct
				grp_members = grp_members + "\"" + current_line[2]+"-"+line_next[1]+object_ports + "\" "
				
			## proccess the p-o
			elif (line_next[0] == "port-object"):

				##Is it a destination range or single port
				if "range" in line_next[1]: 
					object_ports = line_next[2] + "-" + line_next[3]
				## It is an equals "eq"; however it could be a built-in service name or a port number
				else:
					## Let's take care of port numbers first
					if line_next[2].isdigit():
						object_ports = line_next[2]
					else:
						## Otherwise it's a common name http/https/etc)
						try:
							in_cisco_list = cisco_protocol_list.index(line_next[2])
						except ValueError:
							pass
						## convert it to the protocol port number, not common name
						object_ports = cisco_protocol_list[in_cisco_list +1]
				
				## add new object as group member
				## not pretty but correct
				grp_members = grp_members + "\"" + current_line[2] + "-" + current_line[3] + object_ports + "\" "
				
				## Create a unique object
				## first parameter is previous name + a dash + ports  --SHOULD I create an object and pass object for cleaner look?
				## second parameter is tcp/udp
				## third parameter is ports
				object_convert_type_service(current_line[2], current_line[3], object_ports)


			## get next line	
			grp_counter +=1
			line_next = original_lines[counter+grp_counter].split()
		
		## Create new svcGRP and the members
		new_service_group_objects_file.write(grp_name + txt_eol)
		new_service_group_objects_file.write(grp_members + txt_eol + "next" + txt_eol)
		

		## Create a unique object
		## first parameter is previous name + a dash + ports  --SHOULD I create an object and pass object for cleaner look?
		## second parameter is tcp/udp
		## third parameter is ports				
		object_convert_type_service(current_line[2], line_next[1], object_ports)			
			
## Access-List to Policies
	elif (("access-list" == current_line[0]) and ("extended" == current_line[2])):
		
		## Copy object purely for readability 
		acl_line = original_lines[counter].split()
		
		## setup the different elements offsets

		acl_name	 	= acl_line[1]#used for t/s, not sure I need this; may try to append as output-description
		act_offset 		= 3 #permit or deny
		proto_offset 	= 4 # IP/TCP/UDP could be before source/dest or after...really Cisco?
		src_offset		= 5 #could be any, simply setting it to expected
		dst_offset		= 6 #could be any, simply setting it to expected
		svc_offset		= 8 #typically after source/destination // not there if just IP/ICMP
		
		is_acl_enabled	= 1 #1=enabled/0=disabled
		src_is_an_obj	= 1 #most acls use objects
		dst_is_an_obj	= 1 #most acls use objects
		src_addr		= ""
		dst_addr		= ""
		acl_action		= ""
		acl_service		= ""

		
		## active or inactive rule
		if "inactive" in acl_line:
			is_acl_enabled	= 0

		## ACL TYPE is SVC OBJ (first)
		if acl_line[proto_offset] == "object-group":
		## it's a service object first (shakes angry fist at Cisco) & move offsets
			src_offset 		+=1
			dst_offset 		+=1
			svc_offset		= 5
			## svcOBJ Source is ANY
			if ("any" in acl_line[src_offset] or "any4" in acl_line[src_offset]):
			## leave src_offset alone - but not it's not an object
				src_is_an_object = 0
				src_addr = "\"all\""

			## svcOBJ Source is HOST 
			elif ("host" in acl_line[src_offset]):
				src_is_an_object = 0
				src_offset += 1
				src_addr = acl_line[src_offset]
				dst_offset +=1
				##create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset],"")
				
			## svcOBJ Source is OBJECT
			elif ("object" in acl_line[src_offset]):
				src_is_an_object = 1
				src_offset	+= 1
				dst_offset	+= 1
			
			## svcOBJ Source is IP/SUBNET
			else:
				src_is_an_object = 0
				dst_offset +=1
				## need to create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset], acl_line[src_offset+1])
			
			## svcOBJ Destination is ANY
			if ("any" in acl_line[dst_offset] or "any4" in acl_line[dst_offset]):
				dst_is_an_object = 0
				dst_addr = "\"all\""
			
			## svcOBJ Destination is HOST
			elif ("host" in acl_line[dst_offset]):
				dst_is_an_object = 0
				dst_offset += 1
				dst_addr = acl_line[dst_offset]
				##create destination address_object
				create_net_address(acl_line[dst_offset],acl_line[dst_offset],"")

			## svcOBJ Destination is OBJECT
			elif ("object" in acl_line[dst_offset]):
				dst_is_an_object = 1
				dst_offset += 1
				dst_addr = acl_line[dst_offset]
								
			## svcOBJ Destination is IP/SUBNET
			else:
				dst_is_an_object = 0
				#dst_offset += 1	
				## need to create destination address_object
				create_net_address(acl_line[dst_offset], acl_line[dst_offset],acl_line[dst_offset+1])	

		## ACL TYPE is IP
		## need to see if type ICMP fits here
		## no service just src/dst/act-inact
		elif (("ip" in acl_line[proto_offset]) or ("icmp" in acl_line[proto_offset])):
			
			## There is no service, set to 0 
			svc_offset = 0
			
			## IP Source is ANY
			if ("any" in acl_line[src_offset] or "any4" in acl_line[src_offset]):
			## leave src_offset alone - but not it's not an object
				src_is_an_object = 0
				src_addr = "\"all\""
				
			## IP Source is HOST 
			elif ("host" in acl_line[src_offset]):
				src_is_an_object = 0
				src_offset += 1
				src_addr = acl_line[src_offset]
				dst_offset +=1
				##create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset],"")
			
			## IP Source is OBJECT
			elif ("object" in acl_line[src_offset]):
				src_is_an_object = 1
				src_offset	+= 1
				dst_offset	+= 1
				#svc_offset	+= 1
			
			## IP Source is IP/SUBNET
			else:
				src_is_an_object = 0
				dst_offset +=1
				#svc_offset	+= 1
				## need to create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset], acl_line[src_offset+1])
				
			## IP Destination is ANY
			if ("any" in acl_line[dst_offset] or "any4" in acl_line[dst_offset]):
				dst_is_an_object = 0
				dst_addr = "\"all\""
			
			## IP Destination is HOST
			elif ("host" in acl_line[dst_offset]):
				dst_is_an_object = 0
				dst_offset += 1
				dst_addr = acl_line[dst_offset]
				#svc_offset	+= 1
				##create destination address_object
				create_net_address(acl_line[dst_offset],acl_line[dst_offset],"")

			## IP Destination is OBJECT
			elif ("object" in acl_line[dst_offset]):
				dst_is_an_object = 1
				dst_offset += 1
				dst_addr = acl_line[dst_offset]
				#svc_offset	+= 1
				
			## IP Destination is IP/SUBNET
			else:
				dst_is_an_object = 0
				#dst_offset += 1	
				## need to create destination address_object
				create_net_address(acl_line[dst_offset], acl_line[dst_offset],acl_line[dst_offset+1])	
				
			
		## ACL TYPE is TCP/UDP
		## we'll need to convert service
		elif ("tcp" in acl_line[proto_offset] or "udp" in acl_line[proto_offset]) :
			
			####### Now doing Source
	
			## TCP/UDP Source is ANY
			## leave src_offset alone - but not it's not an object
			if ("any" in acl_line[src_offset] or "any4" in acl_line[src_offset]):
				src_is_an_object = 0
				src_addr = "\"all\""
				
			## TCP/UDP Source is HOST
			elif ("host" in acl_line[src_offset]):
				src_is_an_object = 0
				src_offset += 1
				## need to create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset],"")
			
			## TCP/UDP Source is OBJECT
			elif ("object" in acl_line[src_offset]):
				src_is_an_object = 1
				src_offset += 1
				#svc_offset += 1
			## TCP/UDP Source is IP/SUBNET
			else:
				src_is_an_object = 0
				src_offset += 1
				#dst_offset += 1
				##create source address_object
				create_net_address(acl_line[src_offset],acl_line[src_offset],acl_line[src_offset+1])
			
			####### Now doing Destination
			dst_offset = src_offset +1
			
			## TCP/UDP Destination is ANY
			## leave dst_offset alone - but not it's not an object
			if ("any" in acl_line[dst_offset] or "any4" in acl_line[dst_offset]):
				dst_is_an_object = 0
			
			## TCP/UDP Destination is HOST
			elif ("host" in acl_line[dst_offset]):
				dst_is_an_object = 0
				dst_offset += 1
				#svc_offset += 1
				## need to create destination address_object
				create_net_address(acl_line[dst_offset],acl_line[dst_offset],"")
			
			## TCP/UDP Destination is OBJECT
			elif ("object" in acl_line[dst_offset]):
				dst_is_an_object = 1
				dst_offset += 1
				#svc_offset += 1
			
			## TCP/UDP Destination is IP/SUBNET
			else:
				dst_is_an_object = 0
				dst_offset += 1	
				## need to create destination address_object
				create_net_address(acl_line[dst_offset], acl_line[dst_offset],acl_line[dst_offset+1])				
				## Move protocol offset to after destination object

			
			## TCP/UDP Svc is OBJECT/OBJECT-GROUP
			## could be eq/object/object-group/range
			## only range gives us work
			svc_offset = dst_offset+1
			if acl_line[svc_offset] == "range":
				object_ports = line_next[destination_offset + 2] + "-" + line_next[destination_offset + 3]
				object_convert_type_service(acl_line[svc_offset], acl_line[proto_offset], acl_line[svc_offset+1] + "-" +acl_line[svc_offset+2])

				## Create the object
				object_convert_type_service(current_line[2], line_next[1], object_ports)
				## give acl_service a name -- as no name in any offset
				acl_service = acl_line[svc_offset]  + "-" + acl_line[proto_offset] + acl_line[svc_offset+1] + "-" +acl_line[svc_offset+2]
			else:
				svc_offset +=1
			
		## Objects were previously created or built-in services
		## Figure out what protocol & service
		
		#if (acl_line[proto_offset] == "eq" or acl_line[proto_offset]) == "object-group":
		#	proto_offset +=1
		#elif acl_line[proto_offset] == "range":
			## need to create service object
			##
			##
			################################
		#	pass
		

		if src_is_an_obj:
			## order
			### create_fw_policy_fortinet(srcaddr, dstaddr, action, service, is_enabled, rule_number, comment)
			create_fw_policy_fortinet(acl_line[src_offset], acl_line[dst_offset], acl_line[act_offset], acl_line[svc_offset], is_acl_enabled, str(acl_counter), acl_line[1])
			#print ("who:     " + acl_line[1])
			#print ("act:     " + acl_line[act_offset])
			#print ("src:     " + acl_line[src_offset])
			#print ("dst:     " + acl_line[dst_offset])
			#print ("svc:     " + acl_line[svc_offset])
			#print ("active:  " + str(is_acl_enabled))
			#create_fw_policy_fortinet(src_addr, dst_addr, acl_action, acl_service, is_acl_enabled)
		acl_counter +=1
		
## Remove duplicate network objects
new_temp_address_objects_file.close()
new_temp_address_objects_file = open('c:\\convert\\ASA-to-Fortinet-converted-ADD-objects-withdups.txt', 'r')
temp_address_object_list = new_temp_address_objects_file.readlines()
for counter in range(len(temp_address_object_list)):
	found_dup = 0
	next_line_counter = counter+1
	while next_line_counter in range(len(temp_address_object_list)):
		if temp_address_object_list[counter] == temp_address_object_list[next_line_counter]:
			found_dup = 1
		next_line_counter +=1

	if found_dup:
		## skip this instance of object, move on to next line, and reset duplicate status
		pass
		
	else:
		#no duplicate found, write to file
		new_address_objects_file.write(temp_address_object_list[counter])
	counter+=1
	
	
### Close files we had open		
new_temp_address_objects_file.close()
os.remove('c:\\convert\\ASA-to-Fortinet-converted-ADD-objects-withdups.txt')
new_address_objects_file.close()
new_service_objects_file.close()
new_address_group_objects_file.close()	
new_service_group_objects_file.close()
new_nat_objects_file.close()
new_fw_policies_file.close()
print("		")
print("And by the time you've now read all the above")
print("All the items in the left column have been converted!")
