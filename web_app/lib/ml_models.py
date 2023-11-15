import numpy as np
import re
from nltk.util import ngrams
import itertools
from joblib import load

class svm_model:
    def __init__(self):
        pass

    def generate_ngram(self, sentence):
        s = sentence.lower()
        s = ''.join(e for e in s if e.isalnum()) #replace spaces and slashes
        processedList = []
        for tup in list(ngrams(s,3)):
            processedList.append((''.join(tup)))
        return processedList

    def preprocess_sentences_url(self, url):
        alphanum = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0','1','2','3','4','5','6','7','8','9']
        permutations = itertools.product(alphanum, repeat=3)
        featuresDict = {}
        counter = 0
        for perm in permutations:
            f=''
            for char in perm:
                f = f+char;
            featuresDict[(''.join(perm))] = counter
            counter = counter + 1

        X= np.zeros([1, 46656],dtype="int")
        url = url.strip().replace("https://","")
        url = url.replace("http://","")
        url = re.sub(r'\.[A-Za-z0-9]+/*','',url)
        for gram in self.generate_ngram(url):
            try:
                X[0][featuresDict[gram]] = X[0][featuresDict[gram]] + 1
            except:
                pass
        return X    

    def svm_check(self, urls):
        classifier = load('lib/classifiers/url_maliciousness_trained_classifier.joblib') # Load the trained classifier from the file
        returnlist = []

        for w in urls:
            url = w['url']
            pred = classifier.predict(self.preprocess_sentences_url(url))
            if pred == 1:
                w['score'] -= 1
                if 'reason' in w:
                    reason = w['reason'] + ', ML SVM Model'
                    w['reason'] = reason
                else:
                    w['reason'] = 'ML SVM Model'
            returnlist.append(w)   # send back the negative results
        return(returnlist)
    