# with open("well_message.txt",'r') as file:
#     map_data=file.read()
    # json_map = json.loads(map_data)
map_data=[]
with open("well2.txt",'r') as file:
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
    # print(chr(int(map_data[x-1],2)))
    # if int(map_data[x],2) in [71,72]:
    if int(map_data[x],2) not in [130,72,1,32]:
        message+=f' {chr(int(map_data[x],2))}({int(map_data[x],2)}) '

print(message)