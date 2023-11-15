import multiprocessing
from itertools import chain
from pprint import pprint as pp

from lib.url_cleaner import url_cleaner
from lib.url_analyzer import analyze_urls
from lib.utils import utils

class processor_main:
    def __init__(self):
        pass

    def process_chunk(self, args):
        chunk, processing_function = args
        return(processing_function(chunk))

    def chunk_it_up(self, listofthings, num_chunks):
        chunk_size = max(len(listofthings) // num_chunks, 1)  # Ensure chunk size is at least 1
        return [listofthings[i:i + chunk_size] for i in range(0, len(listofthings), chunk_size)]

    def multiprocess_function(self, data, processing_function, num_processes=None):
        if num_processes is None:
            num_processes = multiprocessing.cpu_count()
        chunks = self.chunk_it_up(data, num_processes)  # Split the data into chunks
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map(self.process_chunk, [(chunk, processing_function) for chunk in chunks])
        combined_results = list(chain.from_iterable(results))  # Combine the results efficiently
        return combined_results

    def process_popularity_check(self, data):
        nonpopular_urls = []
        popular_urls = []
        for item in data:
            nonpopular_urls.append(item[0])
            popular_urls.append(item[0])
        return(nonpopular_urls,popular_urls,len(data),len(nonpopular_urls),len(popular_urls))
        
    def main(self, raw_urls):

        # Create an instance of the analyze_urls and urlcleaner classes
        urlcleaner = url_cleaner()
        urlanalyzer = analyze_urls()

        cleaned_urls = self.multiprocess_function(raw_urls, urlcleaner.clean_urls)

        # Tokenize words:
        exploded_urls = self.multiprocess_function(cleaned_urls, urlanalyzer.explode_urls)
    
        ###################
        # one multiprocess function to rule them all: urlanalyzer.processor():
        processed_urls = self.multiprocess_function(exploded_urls, urlanalyzer.processor)
        return(processed_urls)