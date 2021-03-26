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

    columns = []
    data = []
    for table in soup.find_all('table'):
        columns = [th.text for th in table.thead.find_all('th')]
        for tr in table.tbody.find_all('tr'):
            data.append([td.text for td in tr.find_all('td')])

    status_df = pd.DataFrame(data, columns=columns)
    avail_cities = status_df[status_df[columns[-1]] != 'Fully Booked']
    return avail_cities, status_df


state= input("The state you are checking, with the first letter capitalized: ")
input_towns = input("Enter the towns you are checking (for example: New York, NY; Albany, NY)")
sender = input("Sender email: ")
password = input("Sender email password: ")
receiver = input("Receiver email: ")

# Port for SSL
port = 465

towns = input_towns.split(";") if input_towns is not None else None
def clean_up(town):
    city, _, st = town.rpartition(",")
    return city.strip().lower() + "," + st.rstrip()
towns = [clean_up(town) for town in towns] if towns is not None else None

def check_and_send():
    # How often to refresh the page, in seconds
    update = randrange(60, 300)

    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Checking Vaccine Availability in {state} at {curr_time}")
    # Initializes threading (repition / refreshing of website)
    threading.Timer(update, check_and_send).start()

    avail, _ = check_state(state)
    avail_loc = avail.loc[avail[avail.columns[0]].isin(towns), avail.columns[0]] if towns is not None else avail[avail.columns[0]]

    if len(avail_loc.index) > 0:

        print(f"Available Appointment found in {state}; sending emails!")
        # Message in the email.
        cities ="\n".join(avail_loc.values)
        message = f"Subject:CVS Vaccine Availability\n\nAvailable Cities in {state}:\n{cities}"

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)

    else:
        print(f"No availability in {state}; will check again after {str(update)} seconds!")


check_and_send()
