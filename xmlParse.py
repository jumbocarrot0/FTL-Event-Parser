import xml.etree.ElementTree as ET
import random as rand

events = {}
eventNames = []
callableEvents = []
xmlParseReq = {}
equipment = {'systems' : {}, 'cargo' : [], 'missiles' : 0, 'drone parts' : 0, 'fuel' : 0, 'scrap' : 0, }

def FTLEquipmentParse(data):
	global equipment
	for blueprint in data:
		for child in blueprint:
			if child.tag == 'systemList':
				for schild in child:
					if schild.attrib['start'] == 'true':
						equipment['systems'][schild.tag] = int(schild.attrib['power'])
			
			if child.tag == 'weaponList':
				equipment['missiles'] = int(child.attrib['missiles'])
				for wchild in child:
					equipment['cargo'].append(wchild.attrib['name'])
			
			if child.tag == 'droneList':
				equipment['drone parts'] = int(child.attrib['drones'])
				for wchild in child:
					equipment['cargo'].append(wchild.attrib['name'])
			
			if child.tag == 'aug':
				equipment['cargo'].append(child.attrib['name'])
			
			if child.tag == 'fuel':
				equipment['fuel'] = int(child.attrib['amount'])
				
			if child.tag == 'scrap':
				equipment['scrap'] = int(child.attrib['amount'])
				
			if child.tag == 'maxPower':
				equipment['systems']['reactor'] = int(child.attrib['amount'])
				
			if child.tag == 'crewCount':
				for x in range(0, int(child.attrib['amount'])):
					equipment['cargo'].append(child.attrib['class'])
				

def FTLEventTextParse(data):
	text_ids = {'continue': 'Continue...'}
	for child in data:
		if child.tag == 'text' and 'name' in child.attrib:
			text_ids[child.attrib['name']] = child.text
		
	return text_ids

def FTLEventParse(data):
	#print(data)
	for child in data:
		if child.tag == 'eventList':
			if 'name' in child.attrib and data == root:
				eventNames.append(child.attrib['name'])
				callableEvents.append(child.attrib['name'])
				xmlParseReq[child] = child.attrib['name']
				events[child.attrib['name']] = {'eventList':[], 'rand':-1}
				for x in range(0, len(child)):
					events[child.attrib['name']]['eventList'].append(child.attrib['name'] + '_e' + str(x))

		if child.tag == 'event':
			choiceNumber = 0
			if 'name' in child.attrib and data == root:
				events[child.attrib['name']] = {}
				eventNames.append(child.attrib['name'])
				callableEvents.append(child.attrib['name'])
			elif data == root:
				print('ERROR: Unnamed top-level event.')
				continue
			else:
				eventNames.append(xmlParseReq[data])
				number = 0
				while eventNames[-1] in eventNames[:-1]:
					eventNames[-1] = xmlParseReq[data] + '_e' + str(number)
					number += 1
				events[eventNames[-1]] = {}
			for echild in child:
			
				if echild.tag == 'distressBeacon':
					events[eventNames[-1]]['beacon'] = echild.attrib['Distress Signal']
				if echild.tag == 'store':
					events[eventNames[-1]]['store'] = echild.attrib['store']
				if echild.tag == 'repair':
					events[eventNames[-1]]['beacon'] = echild.attrib['Repair Station']
			
				if echild.tag == 'quest' and 'event' in echild.attrib:
					events[eventNames[-1]]['quest'] = echild.attrib['event']
					
				if echild.tag == 'text':
					if 'load' in echild.attrib:
						events[eventNames[-1]]['textList'] = echild.attrib['load']
					elif 'id' in echild.attrib:
						if echild.attrib['id'] in text_ids:
							events[eventNames[-1]]['text'] = [text_ids[echild.attrib['id']]]
						else:
							print('ERROR: id ' + echild.attrib['id'] + ' not found in ' + eventNames[-1])
							events[eventNames[-1]]['text'] = ['id ' + echild.attrib['id'] + ' not found']
							
					else:
						events[eventNames[-1]]['text'] = [echild.text]

				if echild.tag == 'ship' and 'load' in echild.attrib:
					events[eventNames[-1]]['ship'] = echild.attrib['load']

				if echild.tag in ['weapon', 'drone', 'augment']:
					if echild.attrib['name'] == 'RANDOM':
						#placeholder for now
						events[eventNames[-1]]['cargoAdd'] = echild.attrib['name']						
					else:
						events[eventNames[-1]]['cargoAdd'] = echild.attrib['name']

				if echild.tag == 'remove':
					if echild.attrib['name'] == 'RANDOM':
						events[eventNames[-1]]['cargoRemove'] = echild.attrib['name']

				if echild.tag == 'reveal_map':
					events[eventNames[-1]]['reveal_map'] = 'reveal_map'

				if echild.tag == 'modifyPursuit':
					events[eventNames[-1]]['modifyPursuit'] = int(echild.attrib['amount'])

				if echild.tag == 'secretSector':
					events[eventNames[-1]]['secretSector'] = 'secrectSector'

				if echild.tag == 'unlockShip':
					events[eventNames[-1]]['unlockShip'] = echild.attrib['id']

				if echild.tag == 'environment':
					if echild.attrib['type'] in ['nebula', 'asteroid', 'sun', 'storm', 'pulsar', 'PDS']:
						events[eventNames[-1]]['environment'] = echild.attrib['type']
					else:
						print('ERROR: unrecognised environment type in ' + eventNames[-1])

				if echild.tag == 'boarders':
					events[eventNames[-1]]['boarders'] = {'class' : echild.attrib['class'], 'min' : int(echild.attrib['min']), 'max' : int(echild.attrib['max'])}

				if echild.tag == 'crewMember':
					if int(echild.attrib['amount']) < 1:
						if echild.attrib['class'] == traitor:
							if echild.attrib['amount'] == '-1':
								events[eventNames[-1]]['crewTraitor'] = 'crewTraitor'
							else:
								print('ERROR: <crewMember> tag has class traitor and has amount that\'s not -1 in ' + eventNames[-1] + ' event.')
						else:
							print('Warning: <crewMember> tag with values 0 or less in ' + eventNames[-1] + ' event. Use the <removeCrew> tag to remove crew members, or class="traitor" to turn a crew member bad.')
					else:
						skills = ['weapons', 'shields', 'engines', 'pilot', 'combat', 'repair']
						events[eventNames[-1]]['crewMember'] = {'class' : echild.attrib['class'], 'amount' : int(echild.attrib['amount'])}
						if 'all_skills' in events[eventNames[-1]]['crewMember']:
							if 0 < int(echild.attrib['all_skills']) <= 2:
								if int(echild.attrib['all_skills']) == 0:
									print('Advice: Setting a skill to zero in a <crewMember> tag is unnecessary, please remove.')
									for skill in skills:
										events[eventNames[-1]]['crewMember'][skill] = echild.attrib['all_skills']
								else:
									print('Warning: Skill in a <crewMember> tag in ' + eventNames[-1] + ' event is not between 0 and 2.')
							else:
								for skill in skills:
									events[eventNames[-1]]['crewMember'][skill] = echild.attrib['all_skills']
						else:
							for skill in skills:
								if skill in events[eventNames[-1]]['crewMember']:
									if 0 < int(events[eventNames[-1]]['crewMember'].attrib[skill]) <= 2:
										if int(events[eventNames[-1]]['crewMember'].attrib[skill]) == 0:
											print('Advice: Setting a skill to zero in a <crewMember> tag is unnecessary, should be removed.')
											events[eventNames[-1]]['crewMember'][skill] = echild.attrib[skill]
										else:
											print('Warning: Skill in a <crewMember> tag in ' + eventNames[-1] + ' event is not between 0 and 2.')
									else:
										events[eventNames[-1]]['crewMember'][skill] = echild.attrib[skill]
								else:
									events[eventNames[-1]]['crewMember'][skill] = 0
						if 'id' in echild.attrib:
							if echild.attrib['id'] in text_ids:
								events[eventNames[-1]]['crewMember']['name'] = [text_ids[echild.attrib['id']]]
							else:
								print('ERROR: id ' + echild.attrib['id'] + ' not found in ' + eventNames[-1])
								events[eventNames[-1]]['crewMember']['name'] = ['id ' + echild.attrib['id'] + ' not found']
						elif echild.text != '':
							events[eventNames[-1]]['crewMember']['name'] = echild.text
						else:
							events[eventNames[-1]]['crewMember']['name'] = 'Someone'
							
									
				if echild.tag == 'removeCrew':
				
					tagchildren = []
					for rchild in echild:
						tagchildren.append(rchild.tag)
					
					if 'clone' not in tagchildren:
						print('ERROR: <clone> tag not a child of <removeCrew> in event ' + eventNames[-1])
					if 'text' not in tagchildren:
						print('ERROR: <text> tag not a child of <removeCrew> in event ' + eventNames[-1])
						
					if 'clone' in tagchildren and 'text' in tagchildren:
						events[eventNames[-1]]['removeCrew'] = {}
						for rchild2 in echild:
							events[eventNames[-1]]['removeCrew'][rchild2.tag] = rchild2.text
						
						if 'class' in echild.attrib:
							events[eventNames[-1]]['removeCrew']['class'] = echild.attrib['class']
							
						if events[eventNames[-1]]['removeCrew']['clone'] not in ['false', 'true']:
							print('ERROR: <clone> child of <removeCrew> tag in ' + eventNames[-1] + ' event has a value that\'s not true or false.')
							del events[eventNames[-1]]['removeCrew']

				if echild.tag == 'item_modify':
					# fuel, missiles, drone parts
					item_modify = {'steal' : 'false'}
					if 'steal' in echild.attrib:
						item_modify['steal'] = echild.attrib['steal']
					for imchild in echild:
						if imchild.attrib['type'] in ['fuel', 'missiles', 'scrap']:
							item_modify[imchild.attrib['type']] = {'min' : int(imchild.attrib['min']), 'max' : int(imchild.attrib['max']), 'rand' : -1}
						elif imchild.attrib['type'] == 'drones':
							item_modify['drone parts'] = {'min' : int(imchild.attrib['min']), 'max' : int(imchild.attrib['max']), 'rand' : -1}
						else:
							print('Event error: The event ' + eventNames[-1] + ' has an <item> tag with an unrecognisable attribute name.')
					events[eventNames[-1]]['item_modify'] = item_modify

				if echild.tag == 'status':
					workCheck = True
					for attribute in ['type', 'target', 'system', 'amount']:
						if attribute not in echild.attrib:
							workCheck = False
							print('ERROR: ' + attribute + ' attribute not in <status> tag in event ' + eventNames[-1])
							break
					
					if echild.attrib['type'] not in ['limit', 'divide', 'loss', 'clear']:
						print('ERROR: unrecognised "type" attribute in <status> tag in event ' + eventNames[-1])
						workCheck = False
						
					if type(echild.attrib['amount']) is not int:
						if type(echild.attrib['amount']) is float:
							print('Warning: in ' + eventNames[-1] + ' event, amount attribute in <status> tag a float value. Has been rounded down')
						else:
							print('ERROR: in ' + eventNames[-1] + ' event, amount attribute in <status> tag is not an integer.')
							workCheck = False
							
					if workCheck is True:
						events[eventNames[-1]]['status'] = {}
						for attribute in ['type', 'target', 'system', 'amount']:
							events[eventNames[-1]]['status'][attribute] = echild.attrib[attribute]
						
					

				if echild.tag == 'choice':
					events[eventNames[-1]]['choice ' + str(choiceNumber)] = {}
					if 'req' in echild.attrib:
						events[eventNames[-1]]['choice ' + str(choiceNumber)]['req'] = echild.attrib['req']
						if 'lvl' in echild.attrib:
							events[eventNames[-1]]['choice ' + str(choiceNumber)]['lvl_range'] = [echild.attrib['lvl']]
						else:
							events[eventNames[-1]]['choice ' + str(choiceNumber)]['lvl_range'] = [1]
						if 'max_lvl' in echild.attrib:
							events[eventNames[-1]]['choice ' + str(choiceNumber)]['lvl_range'].append(echild.attrib['max_lvl'])
						else:
							events[eventNames[-1]]['choice ' + str(choiceNumber)]['lvl_range'].append(16)
						
					if 'max_group' in echild.attrib:
						events[eventNames[-1]]['choice ' + str(choiceNumber)]['max_group'] = echild.attrib['max_group']
						
					if 'hidden' in echild.attrib:
						events[eventNames[-1]]['choice ' + str(choiceNumber)]['hidden'] = echild.attrib['hidden']
					else:
						events[eventNames[-1]]['choice ' + str(choiceNumber)]['hidden'] = 'false'

					for chochild in echild:
						if chochild.tag == 'text':
							if 'load' in chochild.attrib:
								events[eventNames[-1]]['choice ' + str(choiceNumber)]['text'] = chochild.attrib['load']
							elif 'id' in chochild.attrib:
								events[eventNames[-1]]['choice ' + str(choiceNumber)]['text'] = [text_ids[chochild.attrib['id']]]
							else:
								events[eventNames[-1]]['choice ' + str(choiceNumber)]['text'] = [chochild.text]
						if chochild.tag == 'event':
							if len(chochild) == 0:
								if 'load' in chochild.attrib:
									events[eventNames[-1]]['choice ' + str(choiceNumber)]['event'] = chochild.attrib['load']

								else:
									events[eventNames[-1]]['choice ' + str(choiceNumber)]['event'] = -1

							else:
								events[eventNames[-1]]['choice ' + str(choiceNumber)]['event'] = eventNames[-1] + '_c' + str(
									choiceNumber)
								events[eventNames[-1] + '_c' + str(choiceNumber)] = {}
								xmlParseReq[echild] = eventNames[-1] + '_c' + str(choiceNumber)
					choiceNumber += 1
			
					if choiceNumber >= 5:
						print('Warning: ' + eventNames[-1] + ' has a lot of choice options. FTL may look funky with too many choices in an event.\nEither use choice requirements to make only a few appear at a time, or reduce the number of choices in your event.')
			
			
			if 'choice 0' not in events[eventNames[-1]] and 'text' in events[eventNames[-1]]:
				events[eventNames[-1]]['choice 0'] = {'text': ['Continue'], 'event': -1}	
			elif 'removeCrew' in events[eventNames[-1]]:
				del events[eventNames[-1]]['removeCrew']
				print('ERROR: <removeCrew> tag not used in ' + eventNames[-1] + ' event with other choice tags. <removeCrew> tag deleted in simulation\'s data.')


def FTLTextListParse():
	for child in root:
		if child.tag == 'textList':
			for event in eventNames:
				if 'textList' in events[event]:
					if events[event]['textList'] == child.attrib['name']:
						temp_list = []
						for tchild in child:
							temp_list.append(tchild.text)
						# print(temp_list)
						del events[event]['textList']
						events[event]['text'] = temp_list
						
def errorCheck():
	for event in events:
		if 'text' in events[event]:
			if type(events[event]['text']) is not list:
				print('ERROR: Unidentified textList called by ' + event)
				
		choiceNumb = 0
		while 0 == 0:
			if 'choice ' + str(choiceNumb) in events[event]:
				choiceNumb += 1
			else:
				break
		
		for choice in range(0, choiceNumb):
			if events[event]['choice ' + str(choice)]['event'] != -1:
				if events[event]['choice ' + str(choice)]['event'] not in eventNames:
					print('ERROR: Unidentified eventList called by ' + event)
				

tree = ET.parse('text_events.xml')
root = tree.getroot()

if root.tag != 'FTL':
	print('ERROR: text_events.xml not encapsulated in FTL tag. This tag is required for this parser to work.')
	while 0 == 0:
		input()

text_ids = FTLEventTextParse(root)

tree = ET.parse('events.xml')
root = tree.getroot()

if root.tag != 'FTL':
	print('ERROR: text_events.xml not encapsulated in FTL tag. This tag is required for this parser to work.')
	while 0 == 0:
		input()

FTLEventParse(root)
done = False
while done is False:
	for item in list(xmlParseReq):
		# print('new item')
		FTLEventParse(item)
		del xmlParseReq[item]
	if len(xmlParseReq) == 0:
		done = True

FTLTextListParse()

errorCheck()

tree = ET.parse('ship.xml')
root = tree.getroot()

if root.tag != 'FTL':
	print('ERROR: text_events.xml not encapsulated in FTL tag. This tag is required for this parser to work.')
	while 0 == 0:
		input()

FTLEquipmentParse(root)


command_list = '''
!eventList - bring up a list of loadable events.
!exit - leave event mode or command line.
!help - brings up list of commands.
!load [EVENT_ID] - load an event to play. Must be a named event or eventlist, not a sub-event.
!qlist - bring up a list of loaded quest events.
!qload - load a random quest event to play.
!reload - reloaded previously played event.
!ship - show simulated ship details
'''


print('events loaded\n')
print('Type !help for commands')

eventMode = False
loadedEvent = -1
loadedEventCmd = -1
quests = []
simmedEquipment = equipment
			
def eventEnd(quests):
	global eventMode
	if len(quests) == 0:
		[print('\nEnd of Event (!reload to repeat same event)')]
		eventMode = False
	else:
		if len(quests) == 1:	
			print('\n1 event beacon was placed from this event. do !qload to load a random quest event and !qlist to show a list of loaded quest events. Loading a non-quest event clears this list.')	
		else:
			print('\n' + str(len(quests)) + ' event beacons were placed from this event. do !qload to load a random quest event and !qlist to show a list of loaded quest events. Loading a non-quest event clears this list.')	
		rand.shuffle(quests)
		eventMode = False
		
def item_modifyCalc(event):
	if 'item_modify' in event:
		for item in event['item_modify']:
			if item != 'steal':
				event['item_modify'][item]['rand'] = rand.randint(event['item_modify'][item]['min'], event['item_modify'][item]['max'])
	
def eventListCalc(event):
	if 'eventList' in event:
		event['rand'] = rand.randint(0, len(event['eventList']) - 1)
	
def noChoiceReq():
	global choiceNumb
	global max_groupsSeen
	if events[loadedEvent]['choice ' + str(choiceNumb)]['hidden'] == 'false' and 'max_group' not in events[loadedEvent]['choice ' + str(choiceNumb)]:
		print('X. ' + rand.choice(textLoaded))
		choicesShown.append(choiceNumb + 1)
	if 'max_group' in events[loadedEvent]['choice ' + str(choiceNumb)]:
		max_groupsSeen = max_groupsSeen[:-1]
	choiceNumb += 1
	

while 0 == 0:

	if eventMode is False:
	
	
		command = input('>>> ')

		if command == '!eventList':
			for name in callableEvents:
				print(name)

		if command == '!exit':
			break

		if command == '!help':
			print(command_list)

		if command[:5] == '!load':
			if command[6:] in callableEvents:
				eventMode = True
				loadedEvent = command[6:]
				loadedEventCmd = loadedEvent
				item_modifyCalc(loadedEvent)
				eventListCalc(loadedEvent)
				if loadedEventCmd not in quests and len(quests) > 0:
					quests = []
					print('Quest events cleared')
					simmedEquipment = equipment
				else:
					del quests[quests.index(loadedEventCmd)]
				print('Event loaded.\nEvent mode on.\nUse !exit to leave event mode.\n')
			else:
				print('Invalid ID')
				
		if command == '!qlist':
			if len(quests) > 0:
				for name in quests:
					print(name)
			else:	
				print('No quest events are saved.')
				
		if command == '!qload':
			if len(quests) > 0:
				eventMode = True
				loadedEvent = rand.choice(quests)
				del quests[quests.index(loadedEvent)]
				loadedEventCmd = loadedEvent
				print('Random quest event loaded.\nEvent mode on.\nUse !exit to leave event mode.\n')
			else:
				print('No quest events are saved.')

		if command == '!reload':
			loadedEvent = loadedEventCmd
			if loadedEvent == -1:
				print('No event was previously loaded')
			else:
				eventMode = True
				print('Event reloaded.\nEvent mode on.\nUse !exit to leave event mode.\n')
				
		if command == '!ship':
			print(equipment)
			#To be improved
		
	else:
		
		if 'eventList' in events[loadedEvent]:
			loadedEvent = events[loadedEvent]['eventList'][events[loadedEvent]['rand']]
		
		if 'item_modify' in events[loadedEvent]:
			for item in events[loadedEvent]['item_modify']:
				if item != 'steal':
					if int(events[loadedEvent]['item_modify'][item]['rand']) < 0:
						print('[You lost ' + str(-1 * events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item + ']')
					elif int(events[loadedEvent]['item_modify'][item]['rand']) > 0:
						print('[You got ' + str(events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item + ']')
					simmedEquipment[item] += events[loadedEvent]['item_modify'][item]['rand']
					
		if 'cargoAdd' in events[loadedEvent]:
			simmedEquipment['cargo'].append(events[loadedEvent]['cargoAdd'])
			print('[You got a ' + events[loadedEvent]['cargoAdd'] + ']')
					
		if 'cargoRemove' in events[loadedEvent]:
			del simmedEquipment['cargo'][simmedEquipment['cargo'].index(events[loadedEvent]['cargoRemove'])]
					
		if 'reveal_map' in events[loadedEvent]:
			print('[Your Map has been updated]')
					
		if 'modifyPursuit ' in events[loadedEvent]:
			if events[loadedEvent]['modifyPursuit'] < 0:
				print('[The rebels have been delayed for ' + str(events[loadedEvent]['modifyPursuit'] * -1) + ' jumps]')
			if events[loadedEvent]['modifyPursuit'] > 0:
				print('[The rebels have advanced ' + str(events[loadedEvent]['modifyPursuit']) + ' jumps]')
					
		if 'secretSector ' in events[loadedEvent]:
			print('[Travelling to the secret sector]')
			
		if 'unlockShip' in events[loadedEvent]:
			#placeholder
			print('[You\'ve unlocked the ship with id ' + events[loadedEvent]['unlockShip']+']')
			
		if 'environment' in events[loadedEvent]:
			print('[This beacon has a ' + events[loadedEvent]['environment'] + ']')
			
		if 'boarders' in events[loadedEvent]:
			if events[loadedEvent]['boarders']['class'] == 'random':
				print('['+str(rand.randint(events[loadedEvent]['boarders']['min'], events[loadedEvent]['boarders']['max'])) + ' boarders have entered your ship]')
			else:
				print('['+str(rand.randint(events[loadedEvent]['boarders']['min'], events[loadedEvent]['boarders']['max'])) + ' ' + events[loadedEvent]['boarders']['class'] + ' have entered your ship]')
					
		if 'store' in events[loadedEvent] and events[loadedEvent]['beacon'] != 'store':
			print('[A store is available here]')
			
		if 'beacon' in events[loadedEvent]:
			print('[This beacon has a ' + events[loadedEvent]['beacon'] + ']')
			
		if 'quest' in events[loadedEvent]:
			quests.append(events[loadedEvent]['quest'])
			print('[A quest beacon has been added]')
			
		if 'crewMember' in events[loadedEvent]:
			simmedEquipment['cargo'].append(events[loadedEvent]['crewMember']['class'])
			print('['+events[loadedEvent]['name'] + ' has joined your crew. They are a ' + events[loadedEvent]['crewMember']['class']+']')
			
		if 'crewTraitor' in events[loadedEvent]:
			del simmedEquipment['cargo'][simmedEquipment[rand.randint(0, len(simmedEquipment))]]
			print('[One of your crew members have turned against you!]')
			
		if 'removeCrew' in events[loadedEvent]:
			if 'class' in events[loadedEvent]['removeCrew']:
				if events[loadedEvent]['removeCrew']['class'] in simmedEquipment['cargo']:
					if events[loadedEvent]['removeCrew']['clone'] != 'true' or 'clonebay' not in simmedEquipment['systems'].keys():
						del simmedEquipment['cargo'][simmedEquipment['cargo'].index(events[loadedEvent]['removeCrew']['class'])]
					print('[Your ' + events[loadedEvent]['removeCrew']['class'] + 'has died.]')
				else:
					#may not how it acts in FTL
					if events[loadedEvent]['removeCrew']['clone'] != 'true' or 'clonebay' not in simmedEquipment['systems'].keys():
						del simmedEquipment['cargo'][simmedEquipment[rand.randint(0, len(simmedEquipment))]]
					print('[One of your crew members has died.]')
			else:
				if events[loadedEvent]['removeCrew']['clone'] != 'true' or 'clonebay' not in simmedEquipment['systems'].keys():
					del simmedEquipment['cargo'][simmedEquipment[rand.randint(0, len(simmedEquipment))]]
				print('[One of your crew members has died.]')
				
		if 'status' in events[loadedEvent]:
			limits = {'limit' : 'limited to', 'divide' : 'divided by', 'loss' : 'decreased by', 'clear' : 'cleared'}
			if events[loadedEvent]['status']['target'] == 'player':
				for system in events[loadedEvent]['status']['system']:
					if events[loadedEvent]['status']['type'] == 'clear':
						print('[Your ' + system + '\'s status has been cleared.]')
					else:
						print('[Your ' + system + ' has been ' + limits[events[loadedEvent]['status']['type']] + events[loadedEvent]['status']['amount'] + ' levels.]')
			
			else:
				for system in events[loadedEvent]['status']['system']:
					if events[loadedEvent]['status']['type'] == 'clear':
						print('[Enemy\'s ' + system + '\'s status has been cleared.]')
					else:
						print('[Enemy\'s ' + system + ' has been ' + limits[events[loadedEvent]['status']['type']] + events[loadedEvent]['status']['amount'] + ' levels.]')
					
		if 'text' in events[loadedEvent]:
			textLoaded = events[loadedEvent]['text']
			print(rand.choice(textLoaded) + '\n')
			choiceNumb = 0
			#Selectable choices
			choicesSelectable = []
			#All non-hidden choices
			choicesShown = []
			max_groupsSeen = []
			while 0 == 0:
				if 'choice ' + str(choiceNumb) in events[loadedEvent]:
					
					if events[loadedEvent]['choice ' + str(choiceNumb)]['event'] == -1:
						eventCheck = -1
					elif 'eventList' in events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']]:
						eventCheck = events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']]
						eventCheck = events[eventCheck['eventList'][eventCheck['rand']]]
					else:
						eventCheck = events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']]
				
					if events[loadedEvent]['choice ' + str(choiceNumb)]['event'] != -1:
						eventListCalc(eventCheck)
						item_modifyCalc(eventCheck)
						
					if 'max_group' in events[loadedEvent]['choice ' + str(choiceNumb)]:
						if events[loadedEvent]['choice ' + str(choiceNumb)]['max_group'] not in max_groupsSeen:
							max_groupsSeen.append(events[loadedEvent]['choice ' + str(choiceNumb)]['max_group'])
						else:
							choiceNumb +=1
							continue
						
					if 'req' in events[loadedEvent]['choice ' + str(choiceNumb)]:
						lvl_range = []
						
						for x in range(int(events[loadedEvent]['choice ' + str(choiceNumb)]['lvl_range'][0]), int(events[loadedEvent]['choice ' + str(choiceNumb)]['lvl_range'][1])+1):
							lvl_range.append(x)
							
						if events[loadedEvent]['choice ' + str(choiceNumb)]['req'] in simmedEquipment['systems'].keys():
							if simmedEquipment['systems'][events[loadedEvent]['choice ' + str(choiceNumb)]['req']] not in lvl_range:
								noChoiceReq()
								continue
							
						elif list(simmedEquipment['cargo']).count(events[loadedEvent]['choice ' + str(choiceNumb)]['req']) not in lvl_range:
							noChoiceReq()
							continue
					
					choiceEffectText = ''
					
					if eventCheck != -1:
						if 'item_modify' in eventCheck:
							if eventCheck['item_modify']['steal'] == 'false':
								reqCheck = True
								for item in eventCheck['item_modify']:
									if item != 'steal':
										if -1 * eventCheck['item_modify'][item]['rand'] > simmedEquipment[item]:
											reqCheck = False
											breakc
										
								if reqCheck is False:
									noChoiceReq()
									continue
							
						if events[loadedEvent]['choice ' + str(choiceNumb)]['hidden'] == 'false':
							if 'item_modify' in eventCheck:
								for item in eventCheck['item_modify']:	
									if item != 'steal':
										choiceEffectText += str(eventCheck['item_modify'][item]['rand']) + ' ' + item + '; '
								if len(choiceEffectText) > 0:
									choiceEffectText = choiceEffectText[:-2]
									
							if 'cargoAdd' in eventCheck:
								choiceEffectText += 'Item: ' + eventCheck['cargoAdd'] + '; '
								
							if 'crewMember' in eventCheck:
								choiceEffectText += 'Crew: ' + eventCheck['crewMember']['name'] + ', ' + eventCheck['crewMember']['class'] + '; '
					
					if len(choiceEffectText) > 0:
						choiceEffectText = '    [' + choiceEffectText + ']'
					
					choicesShown.append(choiceNumb + 1)
					textLoaded = events[loadedEvent]['choice ' + str(choiceNumb)]['text']
					print(str(len(choicesShown)) + '. ' + rand.choice(textLoaded) + choiceEffectText)
					choicesSelectable.append(choiceNumb + 1)
					choiceNumb += 1
				else:
					break
			avaliabeCommands = ['!exit']
			for x in range(1, len(choicesSelectable)+1):
				avaliabeCommands.append(str(x))
			command = '-1'
			while command not in avaliabeCommands:
				command = input('Enter choice number: ')
			print('\n')
			if command == '!exit':
				eventMode = False
			else:
				command = int(command) - 1
				if events[loadedEvent]['choice ' + str(command)]['event'] == -1:
					if 'removeCrew' in events[loadedEvent]:
						print(events[loadedEvent]['removeCrew']['text'])
						if events[loadedEvent]['removeCrew']['clone'] == 'true':
							print('[Your crew member has come back!]\n')
						print('1. Continue...')
						avaliabeCommands = ['!exit', '1']
						command = '-1'
						while command not in avaliabeCommands:
							command = input('Enter choice number: ')
						print('\n')
					
					eventEnd(quests)
				else:
					loadedEvent = events[loadedEvent]['choice ' + str(command)]['event']
		else:
			eventEnd(quests)

