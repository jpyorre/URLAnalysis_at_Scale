## This file is used to collect urls from the input file and send them to the processor_main function
from pprint import pprint as pp

from lib.prototype_multiprocessing import processor_main
process = processor_main()

class collect_urls:
    def __init__(self):
        pass

    def filter_items_with_score_minus_one(self,data):
            malicious_urls,benign_urls = [],[]
            for outer_list in data:
                for inner_dict in outer_list:
                    if 'score' in inner_dict and inner_dict['score'] < 0:
                        malicious_urls.append(inner_dict)
                    else:
                        inner_dict['reason'] = 'benign'
                        benign_urls.append(inner_dict)
            return malicious_urls,benign_urls
    
    def get_urls(self,lines):
        raw_urls = []
        for item in lines:
            item = item.strip()
            if not item:
                continue
            item.strip('\r')
            item = item.split(',')
            url = item[0]
            if url == 'url':
                pass
            else:
                raw_urls.append(url)
        return(raw_urls)

    def send_to_processor(self,raw_urls):
        url_results = process.main(raw_urls)

        malicious_urls,benign_urls = self.filter_items_with_score_minus_one(url_results)
        pp(url_results) # This will print to the terminal of the running web app. Turn off if running as a service

        return url_results