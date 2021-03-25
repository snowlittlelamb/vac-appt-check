import smtplib
import ssl
import threading
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
from random import randrange

shoprite_url = 'https://shoprite.reportsonline.com/shopritesched1/program/Imm/patient/advisory'
moderna = 'COVID Moderna Dose 1'
johnson = 'COVID Janssen (J&J) Single Dose '
pfizer = 'COVID Pfizer Dose 1'

chrome_options = Options()
chrome_options.headless = True

def check_vac(vac, zipcode):
    driver = Chrome(options=chrome_options)
    driver.get(shoprite_url)
    while driver.page_source.find("Please select from") < 0:
        if driver.page_source.find("Logged Out") > 0:
            print("You are logged out from the website! Will reconnect in 60s!")
            driver.quit()
            time.sleep(60)
            driver = Chrome(options=chrome_options)
            driver.get(shoprite_url)
        else:
            print("You are waiting in line to enter the website!")
            time.sleep(60)

    driver.find_element_by_xpath(f"//input[@aria-label='{vac}']").click()
    driver.find_element_by_id("zip-input").send_keys(zipcode)
    driver.find_element_by_id("btnGo").click()
    no_avail = driver.page_source.find("There are no locations with available appointments")
    driver.quit()
    return f"zipcode: {zipcode} has {vac}" if no_avail < 0 else None


zipcode= input("What zipcode you want to check? ")
sender = input("Sender email: ")
password = input("Sender email password: ")
receiver = input("Receiver email: ")

# Port for SSL
port = 465

def check_and_send():
    # How often to refresh the page, in seconds
    update = randrange(60, 300)

    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Checking Vaccine Availability in {zipcode} at {curr_time}")
    # Initializes threading (repition / refreshing of website)
    threading.Timer(update, check_and_send).start()

    avail_msg = []
    for vac in [moderna, johnson, pfizer]:
        msg = check_vac(vac, zipcode)
        if msg is not None:
            avail_msg.append(msg)

    if len(avail_msg) > 0:

        print(f"Available Appointment found near {zipcode}; sending emails!")
        # Message in the email.
        avail_vacs_msg = "\n".join(avail_msg)
        message = f"Subject:ShopRite Vaccine Availability\n\n{avail_vacs_msg}"

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)

    else:

        print(f"No availability near {zipcode}; will check again after {str(update)} seconds!")


check_and_send()
