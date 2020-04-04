import xml.etree.ElementTree as ET
import random as rand

events = {}
eventNames = []
callableEvents = []
xmlParseReq = {}
equipment = {'crew' : [], 'systems' : [], 'weaponList' : [], 'droneList' : [], 'missiles' : 0, 'drones' : 0, 'fuel' : 0, 'scrap' : 0, }

def FTLEquipmentParse(data):
	global equipment
	for blueprint in data:
		for child in blueprint:
			if child.tag == 'systemList':
				equipment['systems'] = {}
				for schild in child:
					if schild.attrib['start'] == 'true':
						equipment['systems'][schild.tag] = int(schild.attrib['power'])
			
			if child.tag == 'weaponList':
				equipment['missiles'] = child.attrib['missiles']
				equipment['weaponList'] = []
				for wchild in child:
					equipment['weaponList'].append(wchild.attrib['name'])
			
			if child.tag == 'droneList':
				equipment['drones'] = child.attrib['drones']
				equipment['droneList'] = []
				for wchild in child:
					equipment['droneList'].append(wchild.attrib['name'])
			
			if child.tag == 'fuel':
				equipment['fuel'] = int(child.attrib['amount'])
				
			if child.tag == 'scrap':
				equipment['scrap'] = int(child.attrib['amount'])
				
			if child.tag == 'maxPower':
				equipment['systems']['reactor'] = int(child.attrib['amount'])
				
			if child.tag == 'crewCount':
				for x in range(0, int(child.attrib['amount'])):
					equipment['crew'].append(child.attrib['class'])
				

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
				events[child.attrib['name']] = {'eventList':[]}
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

				if echild.tag == 'item_modify':
					# fuel, missiles, drone parts
					item_modify = {'steal' : 'false'}
					if 'steal' in echild.attrib:
						item_modify['steal'] = echild.attrib['steal']
					for imchild in echild:
						if imchild.attrib['type'] in ['fuel', 'missiles', 'drones', 'scrap']:
							item_modify[imchild.attrib['type']] = {'min' : int(imchild.attrib['min']), 'max' : int(imchild.attrib['max']), 'rand' : -1}
						else:
							print('Event error: The event ' + eventNames[-1] + ' has an <item> tag with an unrecognizable attribute name.')
					events[eventNames[-1]]['item_modify'] = item_modify


				if echild.tag == 'choice':
					events[eventNames[-1]]['choice ' + str(choiceNumber)] = {}
					if 'req' in echild.attrib:
						events[eventNames[-1]]['choice ' + str(choiceNumber)]['req'] = echild.attrib['req']
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
		[print('End of Event (!reload to repeat same event)')]
		eventMode = False
	else:
		if len(quests) == 1:	
			print('1 event beacon was placed from this event. do !qload to load a random quest event and !qlist to show a list of loaded quest events. Loading a non-quest event clears this list.')	
		else:
			print(str(len(quests)) + ' event beacons were placed from this event. do !qload to load a random quest event and !qlist to show a list of loaded quest events. Loading a non-quest event clears this list.')	
		rand.shuffle(quests)
		eventMode = False
		
def item_modifyCalc(event):
	if 'item_modify' in events[event]:
		for item in events[event]['item_modify']:
			if item != 'steal':
				events[event]['item_modify'][item]['rand'] = rand.randint(events[event]['item_modify'][item]['min'], events[event]['item_modify'][item]['max'])
	

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
	
		item_modifyCalc(loadedEvent)
		
		if 'item_modify' in events[loadedEvent]:
			for item in events[loadedEvent]['item_modify']:
				if item != 'steal':
					if int(events[loadedEvent]['item_modify'][item]['rand']) < 0:
						print('You lost ' + str(-1 * events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item + '.\n')
					elif int(events[loadedEvent]['item_modify'][item]['rand']) > 0:
						print('You got ' + str(events[loadedEvent]['item_modify'][item]['rand']) + ' ' + item + '.\n')
		
		if 'eventList' in events[loadedEvent]:
			loadedEvent = rand.choice(events[loadedEvent]['eventList'])
					
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
			choiceNumbShown = 0
			while 0 == 0:
				if 'choice ' + str(choiceNumb) in events[loadedEvent]:
					if events[loadedEvent]['choice ' + str(choiceNumb)]['event'] != -1:
						item_modifyCalc(events[loadedEvent]['choice ' + str(choiceNumb)]['event'])
					if events[loadedEvent]['choice ' + str(choiceNumb)]['hidden'] == 'true':
						if 'req' in events[loadedEvent]['choice ' + str(choiceNumb)]:
							if events[loadedEvent]['choice ' + str(choiceNumb)]['req'] not in (equipment['systems'] and equipment['crew'] and equipment['weaponList'] and equipment['droneList']):
								choiceNumb += 1
								continue
									
						if 'item_modify' in events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']] and events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']]['steal'] == 'true':
							eventCheck = events[events[loadedEvent]['choice ' + str(choiceNumb)]['event']]
							reqCheck = True
							for item in events[eventCheck]['item_modify']:
								if events[eventCheck]['item_modify'][item] > equipment[item]:
									reqCheck = False
									break
							if reqCheck is False:
								choiceNumb +=1
								continue				
					
					textLoaded = events[loadedEvent]['choice ' + str(choiceNumb)]['text']
					print(str(choiceNumbShown + 1) + '. ' + rand.choice(textLoaded))
					choiceNumb += 1
					choiceNumbShown += 1
				else:
					break
			avaliabeCommands = ['!exit']
			for x in range(1, choiceNumb + 1):
				avaliabeCommands.append(str(x))
			command = '-1'
			while command not in avaliabeCommands:
				command = input('Enter choice number: ')
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