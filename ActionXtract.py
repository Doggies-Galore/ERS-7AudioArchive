# Python script to extract action names from RCODE.R and save to Actions.txt

# Open the input file for reading
with open("RCODE.R", "r") as file:
    lines = file.readlines()

# Extract action names
actions = []
for line in lines:
    line = line.strip()
    if 'PRINT "Now playing - ' in line:
        start = line.find('PRINT "Now playing - ') + len('PRINT "Now playing - ')
        end = line.rfind('"')
        action = line[start:end]
        actions.append(action)

# Save to Actions.txt
with open("Actions.txt", "w") as output_file:
    for action in actions:
        output_file.write(action + "\n")
