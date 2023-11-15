import requests,sys
import json
import datetime
from pprint import pprint as pp

file_path = sys.argv[1]

def send_to_api(file_path):
    url = 'http://127.0.0.1:8000/analyze_urls_api'
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'text/csv')}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        result = response.json()
        filename = datetime.datetime.now().strftime('%d%m%Y') + '.json'
        with open('./{}'.format(filename),'w') as file:
            json.dump(result,file)
        return(result)
    else:
        return(False)

results = send_to_api(file_path)
if results != False:
    # Iterate through all items except the last one - it's always the execution time
    for item in results['url_results'][:-1]:  # Skip the last item
        for result in item:  # Now each item is a list of results, iterate through it
            print(f"Domain: {result['domain']}")
            print(f"URL: {result['url']}")
            print(f"Reason: {result['reason']}")
            print(f"Score: {result['score']}")
            print(f"URL Length: {result['url_length']}")

            # Printing other fields...
            print("Possible Actual Words:")
            for word in result.get('possible_actual_words', []):
                print(f" - {word}")

            print("Tokens:")
            for token in result.get('tokens', []):
                print(f" - {token}")

            print("DGA Matches:")
            for key, value in result.get('dga', {}).items():
                print(f" - {key}: {value}")

            print("Levenshtein Matches:")
            for match in result.get('levenshtein_match', []):
                print(f" - {match}")

            print("Punycode Matches:")
            for match in result.get('punycode_match', []):
                print(f" - {match}")

            print("-" * 40)  # Print a divider for readability

    # Print the execution time 
    execution_time_info = results['url_results'][-1]
    print(f"Execution Time: {execution_time_info['Execution Time']}")