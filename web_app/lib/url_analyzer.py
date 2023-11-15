from nltk.corpus import words # for nltk
from spellchecker import SpellChecker # for pyspellcheck (pip3 install pyspellchecker)
import idna # for punycode detection
from fuzzywuzzy import fuzz
import Levenshtein
import re
import requests
import json
import spacy # for check_for_words_without_spaces

from lib.api_calls import apicalls # for api calls
api = apicalls()

from lib.ml_models import svm_model # for ml models
svm = svm_model()

from lib.dga.findDGA import dga # for dga detection
dga_detector= dga()

class analyze_urls:
    def __init__(self):
        pass
    
    
    ###### NOTE:
    # this is where everything is run.
    # If you enable the Investigate or Virustotal Checks, or if you add other features, you need to make sure the variable that is created is passed to the next function.
    # I'll explain in the comment before each function call.

    def processor(self, exploded_urls):
        # svm_classified will be created, holding a dictionary of results:
        svm_classified = svm.svm_check(exploded_urls) # SVM ML Model

        # send svm_classified to dga_check, creating dga_results.
        dga_results = self.dga_check(svm_classified) # Check for DGAs

        #######################
        # TURN ON IF YOU WANT TO USE UMBRELLA INVESTIGATE (and put your API key in lib/investigatetoken.txt):
        # send dga_results to api.negative_urls_from_investigate, creating inv_results.
        # inv_results = api.negative_urls_from_investigate(dga_results)

        #######################
        # TURN ON IF YOU WANT TO USE VIRUSTOTAL (and put your API key in lib/virustotaltoken.txt):
        # send inv_results to api.negative_urls_from_virustotal, creating vt_results.
        # vt_results = api.negative_urls_from_virustotal(inv_results)

        # # send whatever the last variable was to check_for_words_without_spaces, creating the next variable (urls_with_possible_actual_words in this case)
        urls_with_possible_actual_words = self.check_for_words_without_spaces(dga_results) # look for actual words in urls

        # send whatever the last variable was to find_suspicious_words_levenshtein, creating the next variable (suspicious_words_levenshtein in this case)
        suspicious_words_levenshtein = self.find_suspicious_words_levenshtein(urls_with_possible_actual_words) # check via Levenshtein
        
        # send whatever the last variable was to check_for_punycode, creating the next variable (punycode_checked in this case)
        punycode_checked = self.check_for_punycode(suspicious_words_levenshtein)
        
        return(punycode_checked) # return whatever is the last thing
    
    # This takes the words out of the URLs. I called it 'explode_urls' because it sort of 'explodes them':
    def explode_urls(self, urls):
        exploded_urls = []
        for item in urls:
            words = item['url'].split('/')
            url_tokens = []
            for word in words:
                if word:
                    sub_tokens = word.split('.')
                    for i in range(len(sub_tokens)): # need to split on the dash as well if there are any words with that
                        sub_words = sub_tokens[i].split('-')
                        sub_tokens.pop(i)
                        sub_tokens[i:i] = sub_words
                    url_tokens.extend(sub_tokens)
            levenshtein_match = {}
            punycode_match = {}
            dga = {}
            exploded_urls.append({'domain':item['domain'],'url': item['url'],'tokens': url_tokens, 'score': 0,'url_length': sum(len(t) for t in url_tokens),'levenshtein_match':levenshtein_match,'punycode_match':punycode_match,'dga':dga})
        return(exploded_urls)
    
    def dga_check(self,urls):
        dga_detector= dga()
        returnlist = []

        for w in urls:
            domain = w['domain']
            dga_result = dga_detector.classify(domain)
            if dga_result is not None:
                if 'score' in dga_result:
                    w['score'] -= 1
                    w['dga'] = dga_result
                    if 'reason' in w:
                        reason = w['reason'] + ', DGA Detection'
                        w['reason'] = reason
                    else:
                        w['reason'] = 'DGA Detection'
            returnlist.append(w)   # send back the negative results
        return(returnlist)
    
    # NLTK Functions to find English words:
    def is_english_word(self, word):
        english_vocab = set(w.lower() for w in words.words())
        return word.lower() in english_vocab
    
    # if you want to save potential phishing words to a file:
    def write_to_file(self, words_to_analyze):
        with open('phishingwords.txt', 'a') as file:
            for word in set(words_to_analyze):
                file.write(word + '\n')

    def check_for_words_without_spaces(self, word_list):
        nlp = spacy.load("en_core_web_sm") # Load the spaCy English language model
        forbidden_words_list = ['html']
        for item in word_list:
            words_to_analyze = []
            for word in item['tokens']:
                if re.search('[a-zA-Z]', word) and 4 <= len(word) <= 20 and word not in forbidden_words_list:
                    doc = nlp(word)
                    is_recognizable = all(token.is_alpha for token in doc)
                    if is_recognizable:
                        words_to_analyze.append(word)
            
            # self.write_to_file(words_to_analyze) # if you want to save potential phishing words to a file
            item['possible_actual_words'] = words_to_analyze
        return word_list
    
    def find_english_words(self, word_list):
        annotated_words = []
        for sublist in word_list:
            annotated_sublist = []
            for word in sublist['possible_actual_words']:
                if self.is_english_word(word):
                    annotated_sublist.append(f'TRUE: {word}')
                else:
                    annotated_sublist.append(f'FALSE: {word}')
            annotated_words.append(annotated_sublist)
        return annotated_words

    # pyspellcheck - check spelling:
    def find_mispelled_words(self, text):
        spell = SpellChecker()
        returnlist = []
        for w in text:
            listkeeper = []
            for i in w['possible_actual_words']:
                corrected = spell.correction(i)
                if corrected == i:
                    listkeeper.append("Correct: {}".format(i))
                else:
                    listkeeper.append("Incorrect: {} -> {}".format(i,corrected))
            returnlist.append(listkeeper)
        return(returnlist)
    
    def find_suspicious_words_exact_match(self, text):
        # wordlist = ['bank', 'pharm', 'buy']
        wordlist = ['walmart']
        returnlist = []
        for w in text:
            listkeeper = []
            for i in w['possible_actual_words']:
                if any(part in i for part in wordlist): # looking for an exact match of a word from the wordlist
                    listkeeper.append(w)
                    break  # Break out of the inner loop to include the entire word
            if listkeeper:  # Append the list only if it's not empty
                for item in listkeeper: # listkeeper has become a list of lists and containst 0 length entries, so do this to remove them:
                    if len(item) > 1:
                        returnlist.append(item)
        return(returnlist)
    
    def find_suspicious_words_levenshtein(self, urls):
        # to do: Open the much larger word list and use that instead. This list will produce very few results.
        wordlist = ['banking', 'pharma', 'buy', 'walmart', 'citibank', 'hsbc', 'chase', 'wellsfargo', 'citi', 'bankofamer']
        threshold = 2
        returnlist = []

        for w in urls:
            listkeeper = []
            matching_words = []

            for i in w['possible_actual_words']:
                for word in wordlist:
                    if word == 'pharm':
                        threshold = 2
                    else:
                        threshold = 1
                    distance = Levenshtein.distance(word, i)

                    if distance <= threshold and len(i) > 5:
                        levenshtein_match = {}
                        levenshtein_match['match'] = "{},{}".format(i,word)
                        matching_words.append(levenshtein_match)

            if matching_words:
                w['score'] -= 1
                w['levenshtein_match'] = matching_words
                if 'reason' in w:
                    reason = w['reason'] + ', levenshtein'
                    w['reason'] = reason
                else:
                    w['reason'] = 'levenshtein'

            listkeeper.append(w)  # Append the current item to the listkeeper
            returnlist.append(listkeeper)  # Append the listkeeper to the returnlist

        return returnlist
    
    def check_for_punycode(self, urls):
        returnlist = []
        for inner_list in urls:  # Iterate through the outer list
            listkeeper = []
            for w in inner_list:  # Iterate through the inner list
                punycode_words = []
                for i in w['tokens']:
                    try:
                        decoded_word = idna.decode(i)
                        if decoded_word != i:
                            punycode_match = {}
                            # punycode_match['original punycode'] = i
                            punycode_match['match'] = decoded_word
                            punycode_words.append(punycode_match)
                    except:
                        pass
                if punycode_words:
                    w['score'] -= 1
                    w['punycode_match'] = punycode_words
                    if 'reason' in w:
                        reason = w['reason'] + ', punycode'
                        w['reason'] = reason
                    else:
                        w['reason'] = 'punycode'

                listkeeper.append(w)  # Append the current item to the listkeeper

            returnlist.append(listkeeper)  # Append the listkeeper to the returnlist
        return returnlist