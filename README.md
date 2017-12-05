# chatbot
TensorFlow = 1.3
Python: 2.7

Generate Data :


```
	python DeterministicGenerator.py test.gram 
  
```


Pre-processing (requires data generation) :


```
	python data_preprocessing.py
  
```

* navigate to sqs dir
The CNN has been trained and the latest checkpoint for the training can be downloaded from the following link:
https://drive.google.com/open?id=1aTpWLqj0md1Xm22oSZNCbFgCdYHTxFOD

This file contains the latest checkpoint and the labels in the josn format. It also contains the information regarding word count and this folder needs to be placed in the sqs directory.

Predict CNN


```
    python predict.py 

```

For Sequence to Sequence Generator 

1. download trained model from: https://drive.google.com/open?id=1Ths1P1OPSTV6TGClo5vMmJPTJijFRh-L
2. Unzip this in sqs/ckpt/cornell_corpus folder






Run on python 2.6/2.7 from here

Slackbot :

```
pip install slackclient
```

For NER:

```
pip install git+https://github.com/mit-nlp/MITIE.git
```

Also download :

https://www.dropbox.com/s/d4ncdbg88j4zzvs/new_ner_model.dat?dl=0
https://www.dropbox.com/s/3yhg2fm9qnzxu5y/total_word_feature_extractor.dat?dl=0

Make sure they are all in the same directory.

```


python starterbot.py

```







