# FTL-Event-Parser
A program to read XML code from the game FTL:Faster Than Light and create an event simulation.


Features so far:
- Can interpret events from a file and load them in a simulation
- Can handle textLists and eventLists
- Can handle text ids and standard text formatting (i.e. <text id="[ID]"/> and <text>[TEXT]</text>)
- Can interpret quest beacons and continue an event as if you went to said beacon
- Can interpret if a ship is at a beacon (but not if its hostile)
- Can interpret every 'effect' tag, including <item_modify>, <weapon> and <removeCrew>.
- Can interpret various beacon signals (store, distress and repair)
- Simulation can interpret choice requirements
- Has a custom-made command line with various commands
- A basic error checker

Essentially it can handle the bulk of an event's structure, choices, randomisation, etc.


Features to implement:
- Ship events (surrenders, dead crew, etc.)
- AutoReward tag (once I figure out how it works *precisely*)
- Damage tag (kinda just forgot about it)
- Make things nicer (such as not making a person race 'random'. This is hard without reading a big blueprints.xml file)
- More expansive error checker
- A GUI (maybe)


The plan is once I can build a program to simulate an event from XML, then I can reverse the process and create a program that can create an event and export into XML. The event creator will definitely have a GUI.