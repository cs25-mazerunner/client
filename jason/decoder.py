# with open("well_message.txt",'r') as file:
#     map_data=file.read()
    # json_map = json.loads(map_data)
map_data=[]
with open("well_message.txt",'r') as file:
    for line in file:
        comment_split=line.split("#")
        value=comment_split[0].strip()
        if value=='':
            continue
        map_data.append(value)
# map_data=map_data.split()
# print(map_data)

message=''
for x in range(len(map_data)):
    if int(map_data[x],2)==72:
        message+=chr(int(map_data[x-1],2))

print(message)