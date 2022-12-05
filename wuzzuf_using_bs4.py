import time
from bs4 import BeautifulSoup
import requests
import selenium
import scrapy
import mechanicalsoup
import csv
from itertools import zip_longest
import os
from selenium.webdriver.common.by import By
from selenium import webdriver
import re

# creating empty lists
jobs_titles = []
companies_names = []
locations_names = []
new_dates = []
old_dates = []
posted_date = []
pages_links = []
jobs_salaries = []
job_requirement = []
jobs_type = []
job_description = []
job_requirements = []
salary = []
experience = []


def get_searching_url():
    # Getting input from user to search for a specific role
    searching_keyword = input("What to search for ?\n")
    url = "https://wuzzuf.net/jobs/egypt"
    searching_browser = mechanicalsoup.StatefulBrowser()
    searching_browser.open(url)
    searching_browser.select_form('form[action="https://wuzzuf.net/search/jobs/"]')
    searching_browser["q"] = str(searching_keyword)
    searching_browser.submit_selected()
    searching_page_url = searching_browser.get_url()
    return searching_page_url , searching_keyword

# defining a function to return job requirements , requirements , salary and experience needed
def get_job_details(url,browser) :
    browser.get(url)
    description = browser.find_element(By.CLASS_NAME,'css-1uobp1k')
    requirements = browser.find_element(By.CLASS_NAME,'css-1t5f0fr')
    details = browser.find_elements(By.XPATH,'//span[@class="css-4xky9y"]')
    return description.text, requirements.text, details[3].text, details[0].text

def get_page_information(url,browser) :

    # Creating BeautifulSoup object
    response = requests.get(url,timeout=3000).text
    bs_object = BeautifulSoup(response,"html.parser")

    # extracting data from website
    opportunites = bs_object.find_all("h2", class_ = "css-m604qf" )
    companies = bs_object.find_all("a", class_ = "css-17s97q8" )
    locations = bs_object.find_all("span", class_ = "css-5wys0k" )
    date_new = bs_object.find_all("div", class_ = "css-4c4ojb" )
    date_old = bs_object.find_all("div", class_ = "css-do6t5g" )
    date = [*date_new, *date_old]
    links = bs_object.find_all("a", { "class" : "css-o171kl" , "rel":"noreferrer" } )
    types = bs_object.find_all("span", class_ = "css-1ve4b75 eoyjyou0" )

    # looping over extracted lists to get required info into new lists
    for i in range(len(opportunites)) :
        jobs_titles.append(opportunites[i].text)
        companies_names.append(companies[i].text.strip("-").strip(" "))
        locations_names.append(locations[i].text.strip(" "))
        posted_date.append(date[i].text)
        link = "https://wuzzuf.net"+links[i].attrs["href"]
        pages_links.append(link)
        description, requirements, details_1, details_2 = get_job_details(link,browser)
        job_description.append(str(description))
        job_requirements.append(str(requirements))
        jobs_salaries.append(details_1)
        experience.append(details_2)
        jobs_type.append(types[i].text)

# Looping for extracting info from other pages
searching_url , search_keyword = get_searching_url()
browser = webdriver.Chrome()
browser.maximize_window()
browser.get(searching_url)
total_jobs = int(browser.find_element(By.TAG_NAME,'strong').text)

if total_jobs > 0:
    click_next_button = total_jobs//15
    for i in range(click_next_button+1):
        current_url = browser.current_url
        get_page_information(current_url,browser)
        browser.get(current_url)
        try :
            next_button = browser.find_elements(By.XPATH, '//button[@class="css-zye1os ezfki8j0"]')[-1]
            next_button.click()
        except :
            break
    browser.close()
    # exporting extracted data into csv file
    current_directory = os.getcwd()
    file_name = current_directory + "\{}.csv".format(str(search_keyword))
    file_list = [jobs_titles, experience, locations_names, posted_date, jobs_salaries, companies_names, jobs_type,job_description, job_requirements, pages_links]
    exported = zip_longest(*file_list)
    with open(file_name, "w", newline='') as my_file:
        wr = csv.writer(my_file)
        wr.writerow(["job title", "Experience Needed", "Location", "Posted date", "Salary", "Companiey", "Job type",
                     "Description", "Requirements", "Job link"])
        wr.writerows(exported)
    print("All available jobs for {} are extracted successfully".format(search_keyword))

else :
    browser.close()
    print("Can't find jobs for {}".format(search_keyword))