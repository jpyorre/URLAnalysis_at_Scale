#### This is a Flask web app, running on top of FastAPI. It takes in a CSV file of URLs that it runs through various processes to determine if a URL is malicious or not.

##### It's in active development. A website will be set up soon for demo purposes, but you can easily set it up to test on your own using the following instructions.

## To see a presentation on this, visit https://pyosec.com

Note: This was built using multiple methods for optimization. One version of this web app use AWS Lambdas for its functions while another version uses RabbitMQ to send URLs to process to multiple physical machines in other locations in order to make use of their multiprocessing. The code in this repository only uses multiprocessing. I will eventually document the setup for the other versions - it's just a little complex to put the three separate options in one repository and still make it easy for anyone to try running their own version of this web app/api.

This was built to run on python 3.11

## Note:
Currently, the function that reads in a CSV file is hard coded to a specific file layout that has two columns. The columns are labeled: 'url' and 'label'. The function that reads this in is called `get_urls` in `/lib/collect_urls`.

Soon, I'll adjust this to be more flexible. I'll either:

1. Specify that uploaded CSV files need to be in a certain format

or

2. Do some sort of regex magic to find any column that contains URLs or domains.

Just note that until I get to it, you may need to adjust the `get_urls()` function to open your CSV correctly. It's a pretty easy thing to change.

It starts in the app.py file, under one of the two routes (`/analyze_urls` or `analyze_urls_api`)

```
contents = await file.read() # this line reads in the file
lines = contents.decode("utf-8").split('\n')    # this line takes the csv and puts each line into a list
raw_urls = collect_urls.get_urls(lines) # send the list to the collect_urls function
```
Modify the `collect_urls` function to read your data correctly:

## Setup:

Install the en_core_web_sm to use the check_for_words_without_spaces function (must only be done once)

```python -m spacy download en_core_web_sm```


## customization:

In `lib/url_analyzer.py`, the `processor()` function runs through all the detection methods. Check that section out to see how to add new things or modify/remove things.

In `lib/url_analyzer.py`, the `find_suspicious_words_levenshtein()` function uses a list that's created in the function. That list is fairly small (for testing purposes). Use a wordlist containing brands you're interested in instead. I will change this soon to open a wordlist instead.

Code to create wordlists, as well as a few wordlists from the phishtank corpus are in:

`utilities/get_actual_words_from_phishing_words/wordlists`

## Popular domains file:

If you want to keep the file containing the list of most popular domains up to date, it's `lib\top-1m.csv`. This is from the free Cisco Umbrella Top 1 Million list. Either download it manually or set up a process to download it regularly.

# Installation/Setup:

## This app uses mongodb to store results so it doesn't have to look things up again, providing faster service.

If testing, a script in the utilities folder 'clear_database.py' can be used to delete the contents in the database.

## Setting up mongodb:

### OSX Instructions (visit mogodb's website for linux or windows instructions): 

```
brew tap mongodb/brew
brew install mongodb-community@7.0
```

#### Permissions: 

```
sudo chown -R yourusername /opt/homebrew/var/log/mongodb
```

#### Start: 

```
brew services start mongodb-community@7.0
```

#### View running services:

```
brew services list
```

#### Stop: 

```
brew services stop mongodb-community@7.0
```

#### View logs while its working:  

```
tail -f /opt/homebrew/var/log/mongodb/mongo.log
```

### You can in a virtual environment if you want:

```
python3 -m venv venv
source venv/bin/activate
```

#### Install requirements:

```
pip3 install -r requirements.txt
```

### Run the app:

```
uvicorn app_fastapiversion:app --reload
```

Visit in your browser:
http://127.0.0.1:8000


# Using the API:

It's not only a web app, but also an API. A script to send a CSV to the API is in the utilities/api folder.
At the moment, the api script saves the results from the web server to a json file named DDMMYYYY.json. The read_saved_json.py will read that file (you have to give it the filename when running) and can be customized to display whatever is important to you.

The api_client.py can be modified to send streaming data if needed.