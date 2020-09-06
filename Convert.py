#!/usr/bin/env python
# coding: utf-8

import os
import copy
f = open("input.txt",encoding='utf8')
line = f.readline()
df = []
while line: 
    line = line[:-1]
    if len(line) == 0:
        line = f.readline()
        continue
    df.append(line.split(' ',1))
    line = f.readline()
f.close()
df.pop()

theme_list = []  
num = 0
for i in df:
    if i[0]=='##':
        theme_list.append(num)
    num += 1

branch_list = []
num = 0
for i in df:
    if i[0]=='###':
        branch_list.append(num)
    num += 1
branch_list.append(num)

total_list = theme_list + branch_list
total_list.sort()
structured = []
cu_theme = []
for i, element in enumerate(total_list):
    if element in theme_list:
        structured.append(copy.deepcopy(cu_theme))
        cu_theme = []
    elif element in branch_list:
        pos = branch_list.index(element)
        if pos < len(branch_list) - 1 and total_list[total_list.index(branch_list[pos+1]) - 1] not in theme_list:
            cu_theme.append(df[branch_list[pos] : branch_list[pos+1]])
        elif pos < len(branch_list) - 1:
            cu_theme.append(df[branch_list[pos] : branch_list[pos+1] - 1])
structured.append(copy.deepcopy(cu_theme))
structured = structured[1:]

def convert_relation(relation):
    r = relation.lower()
    if r == 'xw':
        return 'xWant'
    elif r == 'xn':
        return 'xNeed'
    elif r == 'xi':
        return 'xIntent'
    elif r == 'xa':
        return 'xAttr'
    elif r == 'xe':
        return 'xEffect'
    elif r == 'xr':
        return 'xReact'
    elif r == 'ow':
        return 'oWant'
    elif r == 'or':
        return 'oReact'
    elif r == 'oe':
        return 'oEffect'
    elif r == 'oa':
        return 'oAttr'

data = []
for num, i in enumerate(structured):
    theme = df[theme_list[num]][1]
    for j in i:
        father = theme
        for k in j:
            data.append([father, convert_relation(k[1].split(' ', 1)[0]), k[1].split(' ', 1)[1]])
            father = k[1].split(' ', 1)[1]

from pandas.core.frame import DataFrame
output = DataFrame(data, columns=['event', 'relation', 'inference'])
output.to_excel('output.xlsx', index=False)