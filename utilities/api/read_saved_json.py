import json
import time
import sys
from pprint import pprint as pp
input_file = sys.argv[1]
with open(input_file, 'r') as file:
    results = json.load(file)

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
        time.sleep(0.025)

    # Print the execution time (assumed to be the last item)
    execution_time_info = results['url_results'][-1]
    print(f"Execution Time: {execution_time_info['Execution Time']}")