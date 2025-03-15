import os
import django
import urllib.parse
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_scraper.settings')
django.setup()

from jobs.models import Job  # Import Job model
import json

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from random import randint

from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import sys

# Get job title from the command-line argument
if len(sys.argv) > 1:
    job_title = sys.argv[1]
else:
    job_title = input("Enter the job title: ")  # Fallback for manual testing
website = """
#########################################
#           WEBSITE: naukri.com          #
######################################### 
"""
print(website)
start_time = datetime.now()
print('Crawl starting time : {}' .format(start_time.time()))
print()

def generate_url(job_title, index):
    formatted_title = job_title.lower().replace(" ", "-")  # Convert to lowercase and replace spaces with '-'
    formatted_title = urllib.parse.quote(formatted_title)  # Ensure URL encoding for special characters
    return f"https://www.naukri.com/{formatted_title}-jobs-in-india-{index}" if index > 1 else f"https://www.naukri.com/{formatted_title}-jobs-in-india"

def extract_rating(rating_a):
    if rating_a is None or rating_a.find('span', class_="main-2") is None:
        return "None"
    else:
        return rating_a.find('span', class_="main-2").text

def save_to_database(job_data):
     job = Job.objects.create(
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        location=job_data["location"],
        rating=job_data["rating"],
        experience=job_data["experience"],
        application_link=job_data["application_link"],
        all_tech_stack=",".join(job_data["all_tech_stack"])
    )
     job.save()
     print(f"Saved job: {job.job_title} at {job.company_name}")
def parse_job_data_from_soup(page_jobs):
    api_url = "http://127.0.0.1:8000/api/jobs/"
    
    for job in page_jobs:
        job = BeautifulSoup(str(job), 'html.parser')
        row1 = job.find('div', class_="row1")
        row2 = job.find('div', class_="row2")
        row3 = job.find('div', class_="row3")
        row5 = job.find('div', class_="row5")
        
        job_title = row1.a.text
        # print(row2.prettify())
        company_name = row2.span.a.text
        rating_a = row2.span
        rating = extract_rating(rating_a)
        
        job_details = row3.find('div', class_="job-details")
        ex_wrap = job_details.find('span', class_="exp-wrap").span.span.text
        location = job_details.find('span', class_="loc-wrap ver-line").span.span.text

        application_link = row1.a['href']

        all_tech_stack = []
        for tech_stack in row5.ul.find_all('li', class_="dot-gt tag-li "):
            tech_stack = tech_stack.text
            all_tech_stack.append(tech_stack)

        job_data = {
            "job_title": job_title,
            "company_name": company_name,
            "rating": rating,
            "experience": ex_wrap,
            "location": location,
            "application_link": application_link,
            "all_tech_stack": all_tech_stack
        }
         # Convert job data to JSON
        job_json = json.dumps(job_data)
        save_to_database(job_data)
        # Use Selenium to execute JavaScript fetch API call
        js_script = f"""
        fetch("{api_url}", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({job_json})
        }})
        .then(response => response.json())
        .then(data => console.log("Success:", data))
        .catch(error => console.error("Error:", error));
        """
        
        driver.execute_script(js_script)  # Execute the API request


options = webdriver.ChromeOptions() 
options.headless = True 
driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

start_page = 1
# edit the page_end here
page_end = 2
for i in range(start_page, page_end):
    print(i)
    job_title = input("Enter the job title: ")
    url = generate_url(job_title, i)
    driver.get(url)
    # sleep for 5-10 seconds randomly just to let it load
    sleep(randint(5, 10))
    get_url = driver.current_url
    if get_url == url:
        page_source = driver.page_source

    # Generate the soup
    soup = BeautifulSoup(page_source, 'html.parser')
    page_soup = soup.find_all("div", class_="srp-jobtuple-wrapper")
    parse_job_data_from_soup(page_soup)

driver.quit()
end_time = datetime.now()