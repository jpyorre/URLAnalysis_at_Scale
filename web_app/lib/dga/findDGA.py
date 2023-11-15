import math
import collections

class dga():
    
    def __init__(self):
        self.unigram_alexa_dict= self.load_gram_file("lib/dga/unigram.count")
        self.bigram_alexa_dict= self.load_gram_file("lib/dga/bigram.count")
        self.limit_min= 100.0
        self.limit_max= 200.0

    def load_gram_file(self, f):
        d=collections.defaultdict(int)
        for line in open(f, "r"):
            line = line.strip()
            gram, count = line.split(" ")
            d[gram]= int(count)
        return d

    def classify(self, domain):
        domain_with_no_tld = domain.split(".")[0]
        _perplexity = self.perplexity(domain_with_no_tld)
        _entropy = self.entropy(domain_with_no_tld)
        score= _perplexity + _entropy
        dga_result = {}
        dga_result = {'score': int(score), 'perplexity': int(_perplexity), 'entropy': int(_entropy)}
        if score >= self.limit_min:# and score <= self.limit_max:
            return dga_result
        else:    
            pass

    def load_gram_file(self, f):
        d={}
        for line in open(f, "r"):
            line = line.rstrip('\n')
            gram, count=line.split()
            d[gram] = int(count)
        return d

    # Calculate Perplexity of string
    def perplexity(self, string):
        N = len(string)
        pp = 1
        _perplexity = 0.0
        
        unigrams = list(string)
        try:
            for i in range (0,len(unigrams)-1):
                bigram_elem = unigrams[i]+unigrams[i+1]
                bigram_elem_freq = 1
                unigram_elem_freq = 1
 
                if(self.bigram_alexa_dict[bigram_elem]):
                    bigram_elem_freq = self.bigram_alexa_dict[bigram_elem]
                
                if(self.unigram_alexa_dict[unigrams[i]]):
                    unigram_elem_freq = self.unigram_alexa_dict[unigrams[i]]
                
                if (unigram_elem_freq <1):
                    unigram_elem_freq = 1
                
                p = unigram_elem_freq*1.0/bigram_elem_freq
                
                if(p==0):
                    p=1
                pp*=p

                _perplexity = pp**(1.0/(N-1))
                
                
                if(_perplexity>100.0):
                    _perplexity = 100.0
                else:
                    _perplexity=_perplexity
        except:
            a=1
        
        return _perplexity

    # Calculates the entropy of a string
    def entropy(self, string):
        
        # get probability of chars in string
        prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]
        
        # calculate the entropy
        entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])
        
        if(entropy>5.0):
            entropy = 5.0
        else:
            entropy*=20
        return entropy