# FTL-Event-Parser
A program to read XML code from the game FTL:Faster Than Light and create an event simulation.


Features so far:
- Can interpret events from a file and load them in a simulation
- Can handle textLists and eventLists
- Can handle text ids and standard text formating (i.e. <text id="[ID]"/> and <text>[TEXT]</text>)
- Can interpret quest beacons
- Can interpret if a ship is at a beacon (but not if its hostile)
- Can interpret the <item_modify> tag
- Can interpret various beacon signals (store, distress and repair)
- Simulation can interpret choice requirements
- Has a custom-made command line with various commands
- A basic error checker

Essentially it can handle the bulk of an event's structure, choices, randomisation, etc.


Features to implement:
- Ship events (surrenders, dead crew, etc.)
- Various effects (status, removeCrew, autoReward, etc.)
