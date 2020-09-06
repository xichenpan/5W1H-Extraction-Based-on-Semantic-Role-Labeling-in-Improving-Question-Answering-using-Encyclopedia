# 5W1H Extraction Based on Semantic Role Labeling in Improving Question Answering using EncyclopediaNet
## Environment

(My experiment environment for reference)

* Ubuntu 18.04.4 LTS
* Python 3.8.3
* allennlp 1.1.0
* nltk 3.5

## Dataset

`datasets\csqa_new\csqa_train_subgraph`

## Introduction

### Semantic Role Labeling

I used the model of [Simple BERT Models for Relation Extraction and Semantic Role Labeling (Shi et al, 2019)](https://arxiv.org/abs/1904.05255) to complete this part of the process.

#### Model introduction

![image-20200906182756683.png](https://i.loli.net/2020/09/06/zSBJgsc2AnMWHaD.png)

* The composition of the input sentence: [CLS] sentence [SEP] verb [SEP]
* The input is processed by Bert to get a vector representation
* Input the vector sequence to a Bi-LSTM and get the last hidden layer state in each direction

#### Semantic Role Labeling usage introduction

AllenNLP reimplemented this model and trained it on the CoNLL 2012 dataset.

We can use the pre-trained model provided by AllenNLP like this demo:

```python
from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz")
predictor.predict(
  sentence="Did Uriah honestly think he could beat the game in under three hours?"
)
```

#### Some processes added

##### Sentence completion

Since there are half sentences in the triples in the data set, in order to get better SRL results and 5W1H representation, we need to complete half sentences.

We can use the following rules to complete:

| Relation |              Completion               |
| :------: | :-----------------------------------: |
|  xWant   |  PersonX want to + Original sentence  |
|  xNeed   |  PersonX need to + Original sentence  |
| xIntent  | PersonX intent to + Original sentence |
|  xAttr   |    PersonX is + Original sentence     |
| xEffect  |      PersonX + Original sentence      |
|  xReact  |   PersonX feel + Original sentence    |
|  oWant   |  Others want to + Original sentence   |
|  oReact  |    Others feel + Original sentence    |
| oEffect  |      Others + Original sentence       |

Performance:

|                       Original triples                       |                      Completed triples                       |
| :----------------------------------------------------------: | :----------------------------------------------------------: |
| ["PersonX asks PersonY's parents for one",<br/> 'oReact',<br/> 'good for keeping personx in the know'] | ["PersonX asks PersonY's parents for one",<br/> 'oReact',<br/> 'Others feel good for keeping personx in the know'] |
| ['PersonX plays ___ at the park',<br/> 'oEffect',<br/> 'their dog feels happy it got to exercise and have fun'] | ['PersonX plays ___ at the park',<br/> 'oEffect',<br/> 'their dog feels happy it got to exercise and have fun'] |

##### Verb replacement

Since the verb in SRL can only recognize actual verbs, some verbs such as "be" and "do" cannot be successfully extracted. Therefore, we use the following synonyms to replace "be" and "do", and then use SRL to get result:

| Original verb | Replaced verb |
| :-----------: | :-----------: |
|      be       |    become     |
|      do       |    finish     |

Performance:

|             Different verb             |                          SRl result                          |
| :------------------------------------: | :----------------------------------------------------------: |
|   PersonX is a great tennis player.    |                             None                             |
| PersonX becomes a great tennis player. | [ARG1: PersonX] [V: becomes] [ARG2: a great tennis player] . |
|      PersonX does a lot of work.       |                             None                             |
|    PersonX finishes a lot of work.     |    [ARG0: PersonX] [V: finishes] [ARG1: a lot of work] .     |

### SRL result to 5W1H representation

Since each node in EncyclopediaNet is a simple sentence, we can use some rules to convert the SRL result of the sentence into 5W1H representation.

| 5W1H representation |         SRL result         |
| :-----------------: | :------------------------: |
|        Verbs        |             V              |
|        What         |            ARG1            |
|        Where        |       ARGM-LOC/ARG4        |
|        When         |          ARGM-TMP          |
|         Who         |            ARG0            |
|        Whom         |      ARG2/ARG3/C-ARG0      |
|         Why         |     ARGM-CAU/ARGM-PRP      |
|         How         | ARGM-MNR/ARGM-COM/ARGM-EXT |
|         Neg         |          ARGM-NEG          |

### EncyclopediaNet Construction

Generally speaking, when we are carrying out EncyclopediaNet construction, we tend to think in a graphical way.

We can easily edit such graphics in Xmind:

![搜狗截图20200906233757.jpg](https://i.loli.net/2020/09/06/ODy3BKo8VUnSzlt.jpg)

We can use the Python program to convert the graphics into the required format:

| Event                                                        | Relation | Inference                                    |
| :----------------------------------------------------------- | -------- | -------------------------------------------- |
| Students had a bake sale because they desperately needed new sports equipment. | xIntent  | Students intent to buy new sports equipment  |
| Students intent to buy new sports equipment                  | oAttr    | School do not have enough money              |
| School do not have enough money                              | xWant    | Students want to get enough money            |
| Students want to get enough money                            | xWant    | Students want to have a bake sale for school |
| Students had a bake sale because they desperately needed new sports equipment. | xIntent  | Students intent to do sports                 |
| Students intent to do sports                                 | oAttr    | Doing sports can make people being strongger |
| Doing sports can make people being strongger                 | xEffect  | Students can be strongger                    |

## Usage introduction

### 5W1H Extraction

In `Func.py`, we provide function `fill_triple()`, `get5w1h_from_sentence()`, `get5w1h_from_triple()`

* Input a triple to `fill_triple()`, you can get the completed triple
* Input a triple to `get5w1h_from_triple()`, you can get the result of 5W1H extraction of the triple
* Input a sentence to `get5w1h_from_sentence()`, you can get the 5W1H extraction result of the sentence

### EncyclopediaNet Construction

In `Convert.py`, you can save the text file exported by Xmind as `input.txt`, and obtain the required `output.xlsx` after program processing
