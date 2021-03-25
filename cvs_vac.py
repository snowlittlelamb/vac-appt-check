import smtplib
import ssl
import threading
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import pandas as pd
from selenium.webdriver.chrome.options import Options
from random import randrange


def check_state(state):
    chrome_options = Options()
    chrome_options.headless = True
    driver = Chrome(options=chrome_options)

    driver.get('https://www.cvs.com/immunizations/covid-19-vaccine')
    driver.find_element_by_link_text(state).click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    status_dict = dict()

    for table in soup.find_all('table'):
        for row in table.tbody.find_all('tr'):
            city = None
            status = None
            for cell in row.find_all('td'):
                span = cell.find('span')
                if 'status' in span.attrs.get('class'):
                    status = span.text
                else:
                    city = span.text
            if city is not None and status is not None:
                status_dict.update({city: status})

    status_df = pd.Series(status_dict)
    avail_cities = status_df[status_df != 'Fully Booked']
    return avail_cities, status_df


state= input("The state you are checking, with the first letter capitalized: ")
sender = input("Sender email: ")
password = input("Sender email password: ")
receiver = input("Receiver email: ")

# Port for SSL
port = 465

def check_and_send():
    # How often to refresh the page, in seconds
    update = randrange(60, 300)

    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Checking Vaccine Availability in {state} at {curr_time}")
    # Initializes threading (repition / refreshing of website)
    threading.Timer(update, check_and_send).start()

    avail, _ = check_state(state)

    if len(avail.index) > 0:

        print(f"Available Appointment found in {state}; sending emails!")
        # Message in the email.
        cities ="\n".join(avail.index)
        message = f"Subject:CVS Vaccine Availability\n\nAvailable Cities in {state}:\n{cities}"

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)

    else:
        print(f"No availability in {state}; will check again after {str(update)} seconds!")


check_and_send()
