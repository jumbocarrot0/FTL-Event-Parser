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
				equipment['missiles'] = child.attrib['missiles']
				for wchild in child:
					equipment['cargo'].append(wchild.attrib['name'])
			
			if child.tag == 'droneList':
				equipment['drone parts'] = child.attrib['drones']
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
				print('Error: Unnamed top-level event.')
				continue
			else:
				eventNames.append(xmlParseReq[data])
				number = 0
				while eventNames[-1] in eventNames[:-1]:
					eventNames[-1] = xmlParseReq[data] + '_e' + str(number)
					number += 1
				events[eventNames[-1]] = {}
			for echild in child:
			
				if child.tag == 'distressBeacon':
					events[eventNames[-1]]['beacon'] = echild.attrib['Distress Signal']
				if child.tag == 'store':
					events[eventNames[-1]]['store'] = echild.attrib['store']
				if child.tag == 'repair':
					events[eventNames[-1]]['beacon'] = echild.attrib['Repair Station']
			
				if child.tag == 'quest' and 'event' in child.attrib:
					events[eventNames[-1]]['quest'] = echild.attrib['event']
					
				if echild.tag == 'text':
					if 'load' in echild.attrib:
						events[eventNames[-1]]['textList'] = echild.attrib['load']
					elif 'id' in echild.attrib:
						if echild.attrib['id'] in text_ids:
							events[eventNames[-1]]['text'] = [text_ids[echild.attrib['id']]]
						else:
							print('Error: id ' + echild.attrib['id'] + ' not found in ' + eventNames[-1])
							events[eventNames[-1]]['text'] = ['id ' + echild.attrib['id'] + ' not found']
							
					else:
						events[eventNames[-1]]['text'] = [echild.text]

				if echild.tag == 'ship' and 'load' in echild.attrib:
					events[eventNames[-1]]['ship'] = echild.attrib['load']

				if child.tag in ['weapon', 'drone', 'augment']:
					if echild.attrib['name'] == 'RANDOM':
						#placeholder for now
						events[eventNames[-1]]['cargoAdd'] = echild.attrib['name']						
					else:
						events[eventNames[-1]]['cargoAdd'] = echild.attrib['name']

				if child.tag == 'remove':
					if echild.attrib['name'] == 'RANDOM':
						events[eventNames[-1]]['cargoRemove'] = echild.attrib['name']

				if child.tag == 'reveal_map':
					events[eventNames[-1]]['reveal_map'] = 'reveal_map'

				if child.tag == 'modifyPursuit':
					events[eventNames[-1]]['modifyPursuit'] = int(child.attrib['amount'])

				if child.tag == 'secretSector':
					events[eventNames[-1]]['secretSector'] = 'secrectSector'

				if child.tag == 'unlockShip':
					events[eventNames[-1]]['unlockShip'] = child.attrib['id']

				if child.tag == 'environment':
					if child.attrib['type'] in ['nebula', 'asteroid', 'sun', 'storm', 'pulsar', 'PDS']:
						events[eventNames[-1]]['type'] = child.attrib['type']
					else:
						print('ERROR: unrecognised environmenttype in ' + eventNames[-1])

				if child.tag == 'boarders':
					events[eventNames[-1]]['boarders'] = {'class' : child.attrib['class'], 'min' : int(child.attrib['min']), 'max' : int(child.attrib['max'])}

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
				print('Error: Unidentified textList called by ' + event)
				
		choiceNumb = 0
		while 0 == 0:
			if 'choice ' + str(choiceNumb) in events[event]:
				choiceNumb += 1
			else:
				break
		
		for choice in range(0, choiceNumb):
			if events[event]['choice ' + str(choice)]['event'] != -1:
				if events[event]['choice ' + str(choice)]['event'] not in eventNames:
					print('Error: Unidentified eventList called by ' + event)
				

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
	
		simmedEquipment = equipment
	
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
						print('You lost ' + str(-1 * events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item)
					elif int(events[loadedEvent]['item_modify'][item]['rand']) > 0:
						print('You got ' + str(events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item)
					simmedEquipment[item] += events[loadedEvent]['item_modify'][item]['rand']
					
		if 'cargoAdd' in events[loadedEvent]:
			simmedEquipment['cargo'].append(events[loadedEvent]['cargoAdd'])
					
		if 'cargoRemove' in events[loadedEvent]:
			del simmedEquipment['cargo'][simmedEquipment['cargo'].index(events[loadedEvent]['cargoRemove'])]
					
		if 'reveal_map' in events[loadedEvent]:
			print('Your Map has been updated')
					
		if 'modifyPursuit ' in events[loadedEvent]:
			if events[loadedEvent]['modifyPursuit'] < 0:
				print('The rebels have been delayed for ' str(events[loadedEvent]['modifyPursuit'] * -1) + ' jumps.')
			if events[loadedEvent]['modifyPursuit'] > 0:
				print('The rebels have advanced ' str(events[loadedEvent]['modifyPursuit']) + ' jumps.')
					
		if 'secretSector ' in events[loadedEvent]:
			print('Travelling to the secret sector.')
			
		if 'unlockShip' in events[loadedEvent]:
			#placeholder
			print('You\'ve unlocked the ship with id ' + events[loadedEvent]['unlockShip'])
			
		if 'environment' in events[loadedEvent]:
			print('This beacon has a ' + events[loadedEvent]['environment'])
			
		if 'boarders' in events[loadedEvent]:
			if events[loadedEvent]['boarders']['class'] == 'random':
				print(str(rand.randint(events[loadedEvent]['boarders']['min'], events[loadedEvent]['boarders']['max'])) + ' boarders have entered your ship!')
			else:
				print(str(rand.randint(events[loadedEvent]['boarders']['min'], events[loadedEvent]['boarders']['max'])) + ' ' + events[loadedEvent]['boarders']['class'] + ' have entered your ship!')
					
		if 'store' in events[loadedEvent] and events[loadedEvent]['beacon'] != 'store':
			print('A store is available here')
			
		if 'beacon' in events[loadedEvent]:
			print('This beacon has a ' + events[loadedEvent]['beacon'])
			
		if 'quest' in events[loadedEvent]:
			quests.append(events[loadedEvent]['quest'])
			print('A quest beacon has been added')
					
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
										choiceEffectText += str(eventCheck['item_modify'][item]['rand']) + ' ' + item + ', '
								if len(choiceEffectText) > 0:
									choiceEffectText = choiceEffectText[:-2]
									
							if 'cargoAdd' in eventCheck:
								choiceEffectText += 'Item: ' eventCheck['cargoAdd']
					
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
					eventEnd(quests)
				else:
					loadedEvent = events[loadedEvent]['choice ' + str(command)]['event']
		else:
			eventEnd(quests)

