#!/usr/bin/env python
# coding: utf-8
from allennlp.predictors.predictor import Predictor
import re
import copy
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz")

def checkarg0(sen):
    try:
        comps = predictor.predict(sentence=sen)
    except:
        return False
    if comps['verbs'] == []:
        return False
    p = re.compile(r'\[(.*?)\]', re.S)
    comps = re.findall(p, comps['verbs'][0]['description'])
    for i in comps:
        if 'ARG0' in i:
            return True
    return False
def checkverb(sen):
    try:
        comps = predictor.predict(sentence=sen)
    except:
        return False
    if comps['verbs'] == []:
        return False
    p = re.compile(r'\[(.*?)\]', re.S)
    comps = re.findall(p, comps['verbs'][0]['description'])
    for i in comps:
        if 'V' in i:
            return True
    return False
def fill_triple(tri):
    i = copy.deepcopy(tri)
    if checkarg0(i[2]):
        return i
    if i[1] == 'xWant':
        if i[2].split(' ', 1)[0] == 'to':
            i[2] = 'PersonX want ' + i[2]
        else:
            i[2] = 'PersonX want to ' + i[2]
    elif i[1] == 'xNeed':
        if i[2].split(' ', 1)[0] == 'to':
            i[2] = 'PersonX need ' + i[2]
        else:
            i[2] = 'PersonX need to ' + i[2]
    elif i[1] == 'xIntent':
        if i[2].split(' ', 1)[0] == 'to':
            i[2] = 'PersonX intent ' + i[2]
        else:
            i[2] = 'PersonX intent to ' + i[2]
    elif i[1] == 'xAttr':
        if checkverb(i[2]):
            i[2] = 'PersonX ' + i[2]
        i[2] = 'PersonX is ' + i[2]
    elif i[1] == 'xEffect': 
        i[2] = 'PersonX ' + i[2]
    elif i[1] == 'xReact':
        i[2] = 'PersonX feel ' + i[2]
    elif i[1] == 'oWant':
        if i[2].split(' ', 1)[0] == 'to':
            i[2] = 'Others want ' + i[2]
        else:
            i[2] = 'Others want to ' + i[2]
    elif i[1] == 'oReact': 
        i[2] = 'Others feel ' + i[2]
    elif i[1] == 'oEffect': 
        i[2] = 'Others ' + i[2]
    return i
def replacebe(s, one):
    sen = copy.deepcopy(s)
    for be_verb in [' was ', ' were ', ' am ', ' are ', ' been ', ' be ', ' is ', ' being ']:
        if be_verb in sen:
            one[0] = be_verb[1:-1]
            break
    if (any(be_verb in sen for be_verb in [' was ', ' were '])):
        sen = sen.replace(' was ', ' became ')
        sen = sen.replace(' were ', ' became ')
    elif (any(be_verb in sen for be_verb in [' am ', ' are ', ' been ', ' be '])):
        sen = sen.replace(' am ', ' become ')
        sen = sen.replace(' are ', ' become ')
        sen = sen.replace(' been ', ' become ')
        sen = sen.replace(' be ', ' become ')
    elif ' is ' in sen:
        sen = sen.replace(' is ', ' becomes ')
    elif ' being ' in sen:
        sen = sen.replace(' being ', ' becoming ')
    return sen
def replacedo(s, one):
    sen = copy.deepcopy(s)
    for be_verb in [' did ', ' does ', ' do ', ' done ', ' doing ']:
        if be_verb in sen:
            one[0] = be_verb[1:-1]
            break
    if ' did ' in sen:
        sen = sen.replace(' did ', ' finished ')
    elif ' does ' in sen:
        sen = sen.replace(' does ', ' finishes ')
    elif ' do ' in sen:
        sen = sen.replace(' do ', ' finish ')
    elif ' done ' in sen:
        sen = sen.replace(' done ', ' finished ')
    elif ' doing ' in sen:
        sen = sen.replace(' doing ', ' finishing ')
    return sen
def get5w1h_from_sentence(i):
    comps = []
    be_flag = False
    do_flag = False
    p = re.compile(r'\[(.*?)\]', re.S)
    s = predictor.predict(sentence=i)
    one = ['','','','','','','','','False']
    if s['verbs'] == []:
        i = replacedo(i, one)
        do_flag = True
        s = predictor.predict(sentence=i)
        print(i)
        if s['verbs'] == []:
            i = replacebe(i, one)
            be_flag = True
            s = predictor.predict(sentence=i)
            if s['verbs'] == []:
                return one
    comps = re.findall(p, s['verbs'][0]['description'])
    output = []
    for l in comps:
        if 'V' in l and not do_flag and not be_flag:
            one[0] = l.split(' ', 1)[1]
        elif 'ARG1' in l:
            one[1] = l.split(' ', 1)[1]
        elif 'ARGM-LOC' in l or 'ARG4' in l:
            one[2] = l.split(' ', 1)[1]
        elif 'ARGM-TMP' in l:
            one[3] = l.split(' ', 1)[1]
        elif 'ARG0' in l:
            one[4] = l.split(' ', 1)[1]
        elif 'ARG2' in l or 'ARG3' in l or 'C-ARG0' in l:
            one[5] = l.split(' ', 1)[1]
        elif 'ARGM-CAU' in l or 'ARGM-PRP' in l:
            one[6] = l.split(' ', 1)[1]
        elif 'ARGM-MNR' in l or 'ARGM-COM' in l or 'ARGM-EXT' in l:
            one[7] = l.split(' ', 1)[1]
        elif 'ARGM-NEG' in l:
            one[8] = 'True'
    return one
def get5w1h_from_triple(tri):
    a = fill_triple(tri)
    output = []
    output += get5w1h_from_sentence(a[0])
    output.append(a[1])
    output += get5w1h_from_sentence(a[2])
    return output