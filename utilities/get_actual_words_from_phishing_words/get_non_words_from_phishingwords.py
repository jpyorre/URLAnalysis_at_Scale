from nltk.corpus import words # for nltk

# NLTK Functions to find English words:
def is_english_word(word):
    english_vocab = set(w.lower() for w in words.words())
    return word.lower() in english_vocab

# if you want to save potential phishing words to a file:
def write_to_file(words_to_analyze):
    with open('wordlists\misspelled_phishingwords_from_phishtank.txt', 'a') as file:
        for word in set(words_to_analyze):
            file.write(word + '\n')
            
def find_english_words(word_list):
    annotated_words = []
    for word in word_list:
        if is_english_word(word):
            # annotated_words.append(word)
            pass
        else:
            annotated_words.append(word)
            print(word)
    return annotated_words

with open('wordlists\uniquephishingwords_fromphishtank.txt', 'r') as file:
    words_to_analyze = file.read().splitlines()

actual_words = find_english_words(words_to_analyze)
write_to_file(actual_words)