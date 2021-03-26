from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import pandas as pd
from selenium.webdriver.chrome.options import Options
import smtplib
import ssl
import threading
from datetime import datetime
import time
from random import randrange

url = "https://am-i-eligible.covid19vaccine.health.ny.gov/"

input_city = input("What city you want to check? (For Example: New York, NY) ") or "New York, NY"
sender = input("Sender email: ")
password = input("Sender email password: ")
receiver = input("Receiver email: ")

def check_vac(input_city):
    chrome_options = Options()
    chrome_options.headless = True
    driver = Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find('table')
    head = table.find("thead")
    columns = [header.text for header in head.find_all("th")]

    rows = []
    for row in table.tbody.find_all('tr'):
        row_data = [cell.text for cell in row.find_all('td')]
        rows.append(row_data)

    input_city = "New York, NY"
    ny_status = pd.DataFrame(rows, columns=columns)
    city_status = ny_status[(ny_status[columns[-1]] == "Yes") & (ny_status[columns[-2]] == input_city)]
    avail_loc = ",".join(city_status[columns[0]].values) if len(city_status.index) > 0 else None
    return avail_loc, ny_status

# Port for SSL
port = 465

def check_and_send():
    # How often to refresh the page, in seconds
    update = randrange(60, 300)

    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Checking Vaccine Availability in {input_city} at {curr_time}")
    # Initializes threading (repition / refreshing of website)
    threading.Timer(update, check_and_send).start()

    avail_loc, _ = check_vac(input_city)

    if avail_loc is not None:

        print(f"Available Appointment found in {input_city}; sending emails!")
        # Message in the email.
        message = f"Subject:NY State Vaccine Availability\n\nVaccine Appointment Available in {input_city} at {avail_loc}. Check the website for more details {url}"

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)

    else:

        print(f"No availability in {input_city}; will check again after {str(update)} seconds!")


check_and_send()
