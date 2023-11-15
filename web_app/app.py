import time
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI, UploadFile, Request, Response
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.requests import Request

client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection URL
db = client["urlresults"]  # Replace with your database name
collection = db["results"]  # Replace with your collection name

from lib.collect_urls import collect_urls
collect_urls = collect_urls()

from lib.utils import utils
utils = utils()

from lib.url_cleaner import url_cleaner # remove popular domains here
urlcleaner = url_cleaner()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/lib", StaticFiles(directory="lib"), name="lib")
templates = Jinja2Templates(directory="templates")

def insert_into_mongodb(flattened_results):
    for result in flattened_results:
        result.pop("_id", None)
    collection.insert_many(flattened_results) # Save flattened_data to MongoDB

@app.get("/", response_class=HTMLResponse)
async def index_form(request: Request):
    # static_url = request.url_for("static", path="")
    return templates.TemplateResponse("upload.html", {"request": request})#, "static_url": static_url})

def check_existing_url(url): # Check if the URL already exists in the database
    existing_data = collection.find_one({"url": url}, {"_id": 0})
    return existing_data

@app.post('/analyze_urls_api')
async def analyze_urls_api(file: UploadFile, request: Request):
    urls_on_popular_domains = []
    urls_on_un_popular_domains = []
    urls_to_lookup = []
    results_already_in_db = []
    url_results = []

    start_time = time.time()
    contents = await file.read()
    lines = contents.decode("utf-8").split('\n')
    raw_urls = collect_urls.get_urls(lines)
    popularity_results = urlcleaner.remove_popular_domains(raw_urls)
    
    for i in popularity_results:
        if i['result'] == 'popular':
            urls_on_popular_domains.append(i)
        if i['result'] == 'unpopular':
            urls_on_un_popular_domains.append(i)
        # check if already in db and separate into two lists:
    for item in urls_on_un_popular_domains:
        already_in_db = check_existing_url(item['url'])
        if already_in_db:
            results_already_in_db.append(already_in_db) # If the URL exists, append the existing data to results_already_in_db
        else:
            urls_to_lookup.append(item)
    results_already_in_db_to_combine = utils.reconstitute_already_seen(results_already_in_db)
    if len(urls_to_lookup) > 0:
        new_url_results = collect_urls.send_to_processor(urls_to_lookup) # Process new URLs and add them to MongoDB
        flattened_new_data, new_fieldnames = utils.flatten_data(new_url_results) # Flatten new data for display and CSV

        insert_into_mongodb(flattened_new_data) # Write new data to MongoDB

        url_results.extend(new_url_results) # Extend url_results with new data
        
    url_results.extend(results_already_in_db_to_combine) # Extend url_results with existing data
    elapsed_time = time.time() - start_time
    url_results.append({'Execution Time': f"{elapsed_time:.2f} seconds"})
    return {"url_results": url_results}

@app.post('/analyze_urls')
async def processurls(file: UploadFile, request: Request):
    start_time = time.time()
    if file.content_type == "text/csv":
        contents = await file.read()
        lines = contents.decode("utf-8").split('\n')
        urls_to_lookup = []
        results_already_in_db = []
        raw_urls = collect_urls.get_urls(lines)
        popularity_results = urlcleaner.remove_popular_domains(raw_urls)
        urls_on_popular_domains = []
        urls_on_un_popular_domains = []

        for i in popularity_results:
            if i['result'] == 'popular':
                urls_on_popular_domains.append(i)
            if i['result'] == 'unpopular':
                urls_on_un_popular_domains.append(i)
        # check if already in db and separate into two lists:
        for item in urls_on_un_popular_domains:
            already_in_db = check_existing_url(item['url'])
            if already_in_db:
                results_already_in_db.append(already_in_db) # If the URL exists, append the existing data to results_already_in_db
            else:
                urls_to_lookup.append(item)
        # Reconstitute the existing data in db into the same structure as newly searched so that it safely go to the flatten_data function:
        results_already_in_db_to_combine = utils.reconstitute_already_seen(results_already_in_db)

        # Initialize url_results as an empty list
        url_results = []
        # print(urls_to_lookup)
        if len(urls_to_lookup) > 0:
            new_url_results = collect_urls.send_to_processor(urls_to_lookup) # Process new URLs and add them to MongoDB
            flattened_new_data, new_fieldnames = utils.flatten_data(new_url_results) # Flatten new data for display and CSV

            insert_into_mongodb(flattened_new_data) # Write new data to MongoDB

            url_results.extend(new_url_results) # Extend url_results with new data

        url_results.extend(results_already_in_db_to_combine) # Extend url_results with existing data
        flattened_data, fieldnames = utils.flatten_data(url_results) # Flatten all data for CSV and display
        elapsed_time = time.time() - start_time
        url_results.append({'Execution Time': f"{elapsed_time:.2f} seconds"})
        csv_data = utils.generate_csv(flattened_data, fieldnames)
        response = Response(content=csv_data, media_type="text/csv")
        response.headers["Content-Disposition"] = 'attachment; filename=results.csv'
        context = {"request": request, "url_results": url_results, "csv_data": csv_data}
        return templates.TemplateResponse("results.html", context)
    else:
        return HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

@app.get("/download_csv")
async def download_csv(request: Request):
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{current_date}_url_results.csv"
    file_path = 'static/data/results.csv'
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
    }
    return FileResponse(file_path, headers=headers) # Return the file as a response

@app.get('/urls')
async def urls(request: Request):
    cursor = collection.find({}, {"_id": 0}) # Retrieve data from MongoDB, exclude the _id field from the result
    url_results = list(cursor) # Convert the cursor to a list of dictionaries
    return templates.TemplateResponse("savedresults.html", {"request": request, "url_results": url_results})


    
# In your terminal, run:
# uvicorn app:app --reload
# then visit the url listed in the terminal in your browser