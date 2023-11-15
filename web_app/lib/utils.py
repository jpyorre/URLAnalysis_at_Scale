import csv
from datetime import datetime

class utils:
    def __init__(self):
        pass

    # used to make the data into something that can be turned into the downloaded csv file.
    def flatten_data(self, data):
        flattened_data = []
        fieldnames = set()

        for sublist in data:
            for item in sublist:
                if 'Execution Time' in item:
                    continue
                flattened_item = {
                    'dga': item.get('dga', ''),
                    'domain': item.get('domain', ''),
                    'levenshtein_match': item.get('levenshtein_match', ''),
                    'possible_actual_words': ', '.join(item.get('possible_actual_words', [])),
                    'punycode_match': item.get('punycode_match', ''),
                    'reason': item.get('reason', ''),
                    'score': item.get('score', ''),
                    'tokens': ', '.join(item.get('tokens', [])),
                    'url': item.get('url', ''),
                    'url_length': item.get('url_length', ''),
                }

                dga_match = flattened_item.get('dga', [])
                if isinstance(dga_match, list):
                    match_strings = []
                    for match_item in dga_match:
                        match_strings.append(match_item.get('score', ''))
                        match_strings.append(match_item.get('perplexity', ''))
                        match_strings.append(match_item.get('entropy', ''))
                    flattened_item['dga'] = ', '.join(match_strings).replace(',', ' | ')

                levenshtein_match = flattened_item.get('levenshtein_match', [])
                if isinstance(levenshtein_match, list):
                    match_strings = []
                    for match_item in levenshtein_match:
                        match_strings.append(match_item.get('match', ''))
                    flattened_item['levenshtein_match'] = ', '.join(match_strings).replace(',', ' | ')

                punycode_match = flattened_item.get('punycode_match', [])
                if isinstance(punycode_match, list):
                    match_strings = []
                    for match_item in punycode_match:
                        match_strings.append(match_item.get('match', ''))
                    flattened_item['punycode_match'] = ', '.join(match_strings).replace(',', ' | ')
                
                fieldnames.update(flattened_item.keys())
                flattened_data.append(flattened_item)

        return flattened_data, list(fieldnames)

    # take already seen data and turn it into something that can be put into the downloadable csv.
    def reconstitute_already_seen(self, results_already_in_db):
        new_structure_list = []

        for item in results_already_in_db:
            new_item = {
                'domain': item['domain'],
                'url': item['url'],
                'tokens': item['tokens'].split(', '),  # Split tokens by comma and space
                'score': item['score'],
                'url_length': item['url_length'],
                'levenshtein_match': [],
                'punycode_match': [],
                'dga': {},
                'reason': item['reason'],
                'possible_actual_words': item['possible_actual_words'].split(', '),  # Split words by comma and space
            }

            # Handle levenshtein_match if it exists
            if 'levenshtein_match' in item and isinstance(item['levenshtein_match'], dict):
                new_item['levenshtein_match'] = [{'match': key} for key in item['levenshtein_match']]

            new_structure_list.append([new_item])
        return(new_structure_list)

    def generate_csv(self, data, fieldnames):
        if not data:
            return ""
        
        with open('static/data/results.csv', mode='w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            csv_writer.writeheader()
            for row in data:
                csv_writer.writerow(row)