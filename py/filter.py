# coding=utf8
import json
import jsonlines
import re
from utils import formatTag
from utils import bSearch
from sortedcontainers import SortedSet

altRaw=SortedSet()
alt=SortedSet()
tags={}

with jsonlines.open('../data/person.jsonlines') as jl:
    for line in jl:
        m=re.search('中文名= (.+?)\\r', line['infobox']) #简体中文名
        if m:
            key=formatTag(m.group(1))
            altRaw.add((formatTag(line['name']), key)) #人物条目名
            m=re.search('别名=\{(.+?)\}', line['infobox'], flags=re.S) #别名
            if m:
                for i in re.findall('\[(?:[^\]]+?\|)?(.*?)\]', m.group(1)):
                    for j in re.split('[、・,，/]', i):
                        altRaw.add((formatTag(j), key))

altRaw=list(altRaw)
print(len(altRaw))
#remove ambiguous items
altRaw=[altRaw[i] for i in range(len(altRaw)) if (i==0 or altRaw[i][0]!=altRaw[i-1][0]) and (i==len(altRaw)-1 or altRaw[i][0]!=altRaw[i+1][0])]
#remove self-referencing items
altRaw=[i for i in altRaw if i[0]!=i[1]]
print(len(altRaw))

def bindTag(sName):
    fName=formatTag(sName)
    res=bSearch(altRaw, fName)
    if res:
        alt.add((fName,res))
        return res
    return fName

data = json.load(open('../data/subject.json', encoding='utf-8'))

for i in data:
    s=i['year']
    for t in i['tags']:
        name=t['name']
        if s not in tags:
            tags[s]={}
        if name in tags[s]:
            tags[s][name]+=t['count']
        else:
            tags[s][name]=t['count']

with open("../data/tagsRaw.json", "w", encoding='utf-8') as outfile:
    json.dump(tags, outfile, ensure_ascii=False)
tags={}

for i in data:
    s=i['year']
    for t in i['tags']:
        name=bindTag(t['name'])
        if s not in tags:
            tags[s]={}
        if name in tags[s]:
            tags[s][name]+=t['count']
        else:
            tags[s][name]=t['count']
print(len(alt))

with open("../data/tags.json", "w", encoding='utf-8') as outfile:
    json.dump(tags, outfile, ensure_ascii=False)
with open("../data/altNames.json", "w", encoding='utf-8') as outfile:
    json.dump(list(alt), outfile, ensure_ascii=False)
