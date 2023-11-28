import os
import json
import time
import yagmail
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler

class DatabaseManager:
    def __init__(self, urlmongo):
        self.urlmongo = urlmongo

    def insert_into_database(self, jobdata):
        client = MongoClient(self.urlmongo, server_api=ServerApi('1'))
        db = client["OnCampusDB"]
        collection = db["Jobs"]
        collection.delete_many({})
        collection.insert_many(jobdata)
        client.close()
        print('Successfully Inserted!')

    def fetch_all_records(self):
        client = MongoClient(self.urlmongo, server_api=ServerApi('1'))
        db = client["OnCampusDB"]
        collection = db["Jobs"]
        all_documents = list(collection.find({}))
        return all_documents

class WebScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def login(self):
        driver = webdriver.Chrome()
        driver.get('https://tp.bitmesra.co.in/login.html')

        wait = WebDriverWait(driver, 10)

        username_field = wait.until(
            EC.presence_of_element_located((By.ID, 'identity')))
        password_field = wait.until(
            EC.presence_of_element_located((By.ID, 'password')))
        submit_button = wait.until(
            EC.presence_of_element_located((By.NAME, 'submit')))

        username_field.send_keys(self.email)
        password_field.send_keys(self.password)

        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(5)
        submit_button.click()

        job_names = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'py-0')))
        job_link = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//td[@class="no-sort"]//a[2]')))
        job_deadline = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//tr[@role="row"]//td[2]')))

        time.sleep(5)
        records = []
        for job, link, deadline in zip(job_names[11:], job_link, job_deadline):
            records.append({
                'Company_name': job.text,
                'page_link': str(link.get_attribute('href')),
                'deadline': deadline.text
            })

        driver.quit()
        return records

    def scrape_jobs(self):
        # Implementation...
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-setuid-sandbox")

        chrome_options.add_argument("--remote-debugging-port=9222")  # this

        chrome_options.add_argument("--disable-dev-shm-using")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument(r"user-data-dir=.\cookies\\test")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://tp.bitmesra.co.in/login.html')

        wait = WebDriverWait(driver, 10)

        username_field = wait.until(
            EC.presence_of_element_located((By.ID, 'identity')))
        password_field = wait.until(
            EC.presence_of_element_located((By.ID, 'password')))
        submit_button = wait.until(
            EC.presence_of_element_located((By.NAME, 'submit')))

        username_field.send_keys(self.email)
        password_field.send_keys(self.password)

        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(5)
        submit_button.click()

        job_names = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'py-0')))
        job_link = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//td[@class="no-sort"]//a[2]')))
        job_deadline = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//tr[@role="row"]//td[2]')))

        time.sleep(5)
        records = []
        for job, link, deadline in zip(job_names[11:], job_link, job_deadline):
            records.append({
                'Company_name': job.text,
                'page_link': str(link.get_attribute('href')),
                'deadline': deadline.text
            })

        driver.quit()
        return records

class EmailManager:
    def __init__(self, sender, authkey):
        self.sender = sender
        self.authkey = authkey

    def send_status(self, sender, authkey):
                yag = yagmail.SMTP(user=self.sender, password=self.authkey)
                subject = "!!!BOT STATUS!!!"
                content = "The bot is live!"
                yag.send(to='rajpriyanshu7214@gmail.com',
                         subject=subject,
                         contents=content)
                print("Status Sent!")

    def send_mail(self, past_job_data, current_job_data):
        if not past_job_data:
            print("No past job data. Exiting.")

        past_job_ids = set(job['page_link'] for job in past_job_data)
        new_jobs = [
            job for job in current_job_data if job['page_link'] not in past_job_ids
        ]

        if not new_jobs:
            print("No new jobs found. Exiting.")
            return

        sender_mail = self.sender
        auth_key = self.authkey
        yag = yagmail.SMTP(user=sender_mail, password=auth_key)

        for job in new_jobs:
            subject = job['Company_name']
            content = '''   New Job Added! Check T&P Website Right Now!
                            Company Name: {}
                            Deadline: {}
                            Page Link: {}
                        '''
            message = content.format(job['Company_name'], job['deadline'],
                                     job['page_link'])
            yag.send(to='rajpriyanshu7214@gmail.com',
                     subject=subject,
                     contents=message)
            print('Mail Sent!')


class WebAutomation:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)
        self.database_manager = DatabaseManager(self.config.get("urlmongo"))
        self.web_scraper = WebScraper(self.config.get("username"), self.config.get("password"))
        self.email_manager = EmailManager(self.config.get("sender"), self.config.get("authkey"))

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, "r") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            print("Config file not found.")
            return {}

    def run(self):
        past_job_data = self.database_manager.fetch_all_records()
        current_job_data = self.web_scraper.login()
        self.database_manager.insert_into_database(current_job_data)
        self.email_manager.send_mail(past_job_data, current_job_data)

class RunAllDay:
    def __init__(self, web_automation_instance):
        self.web_automation = web_automation_instance
        self.sender = web_automation_instance.config.get("sender")
        self.authkey = web_automation_instance.config.get("authkey")
        self.scheduler = BackgroundScheduler()

    def run_continuous_tasks(self):
        while True:
            self.web_automation.email_manager.send_status(self.sender,self.authkey)
            time.sleep(2700)

    def run_all_day(self):
        continuous_thread = threading.Thread(target=self.run_continuous_tasks)
        continuous_thread.start()

        self.scheduler.add_job(self.web_automation.run, 'interval', hours=1)
        self.scheduler.start()

        try:
            continuous_thread.join()
        except KeyboardInterrupt:
            self.scheduler.shutdown()

if __name__ == "__main__":
    web_automation_instance = WebAutomation("config.json")
    # run_all_day_instance = RunAllDay(web_automation_instance)
    # run_all_day_instance.run_all_day()
    web_automation_instance.run()