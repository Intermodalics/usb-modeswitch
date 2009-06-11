#!/usr/bin/env python

import fileinput

## Common variables
commentBlock = False

configIndex = -1

configList = [{}]

optionMap = {
	'DefaultVendor': ' --default-vendor ',
	'DefaultProduct': ' --default-product ',
	'TargetVendor': ' --target-vendor ',
	'TargetProduct': ' --target-product ',
	'TargetClass': ' --target-class ',
	'MessageEndpoint': ' --message-endpoint ',
	'MessageContent': ' --message-content ',
	'ResponseEndpoint': ' --response-endpoint ',
	'DetachStorageOnly': ' --detach-storage-only ',
	'HuaweiMode': ' --huawei-mode ',
	'SierraMode': ' --sierra-mode ',
	'SonyMode': ' --sony-mode ',
	'ResetUSB': ' --reset-usb ',
	'Interface': ' --interface ',
	'Configuration': ' --configuration ',
	'AltSetting': ' --altsetting '
}

# Go through the whole file
for line in fileinput.input():
        # Take widely commented lines 
	if line[0:4] == '####':
		configIndex += 1
		configList += [{}]
		commentBlock = True
		configList[configIndex]['Comment'] = line
		continue
	if line[0] == '#' and commentBlock:
		configList[configIndex]['Comment'] += line
		continue
	if len(line) < 1:
		commentBlock = False
		continue

	# Take only lines with actual configuration
	if line[0] == ';':
		# We have a variable

		# Where does the variable end ?
		equalPos = line.find('=')
		
		variableName = line[1:equalPos]
		variableContent = line[equalPos+1:-1].strip()
		
		# print variableName,"=",variableContent

		configList[configIndex][variableName] = variableContent

print '''### /etc/udev/rules.d/usb_modeswitch.rules ###
# This file is generated from /etc/usb_modeswitch.conf
#
# For multiply-defined ID, only the first one is uncommented.
# Other ones are available but commented.
#

'''
def um_comAdd(indic, indivConfig, toggle=False):
	if indic in indivConfig:
		if not toggle:
			return optionMap[indic] + indivConfig[indic]
		else:
			return optionMap[indic]
	else:
		return ''

# Now we have everything needed in configList
uniqIds = {}
for indivConfig in configList:
	if 'DefaultVendor' in indivConfig and 'DefaultProduct' in indivConfig:
		uniqId = indivConfig['DefaultVendor'] + ":" + indivConfig['DefaultProduct']
		print indivConfig['Comment'],
		
		print '# Vendor:Product id =',uniqId

		um_commandline  = '/usr/sbin/usb_modeswitch'
		um_commandline += um_comAdd('DefaultVendor',indivConfig)
		um_commandline += um_comAdd('DefaultProduct',indivConfig)
		um_commandline += um_comAdd('MessageEndpoint', indivConfig)
		if 'MessageContent' in indivConfig:
			um_commandline += optionMap['MessageContent'] +  indivConfig['MessageContent'][1:-1]
		um_commandline += um_comAdd('ResponseEndpoint', indivConfig)
		um_commandline += um_comAdd('DetachStorageOnly', indivConfig, True)
		um_commandline += um_comAdd('Interface', indivConfig)

		ruleLine  = 'SUBSYSTEM=="usb", '
		ruleLine += 'SYSFS{idVendor}=="' + indivConfig['DefaultVendor'][2:] +'", '
		ruleLine += 'SYSFS{idProduct}=="' + indivConfig['DefaultProduct'][2:] + '", '
		ruleLine += 'RUN+="' + um_commandline + '"'

		if uniqId not in uniqIds:
			uniqIds[uniqId] = ''
			print ruleLine
		else:
			print '#' + ruleLine
		print '' 

