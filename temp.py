import requests
from bs4 import BeautifulSoup
from re import sub
from decimal import Decimal
import smtplib
import time


def check_price(r):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=1&page=1&sparkline=false"
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    page = page.json()
    out = "current_price"
    price = page[0]["current_price"]
    if price < r:
        send_email(url, price, "decreased")
    elif price > r:
        send_email(url, price, "increased")
    else:
        send_email(url, price, "same")


def send_email(url, price, status):

    gmail_user = "karthikrock854@gmail.com"
    gmail_password = "jsgrdjsdjgoeyexu"

    sent_from = gmail_user
    to = ["miolo@driely.com"]
    subject = "Bitcoin  prce is {}".format(status)
    body = (
        "Hey, why are you waiting buy now at \n\n"
        + "www.krypto.com"
        + "\n\n"
        + "Current price is {}".format(price)
    )

    msg = "Subject: {}\n\n{}".format(subject, body)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail("karthikrock854@gmail.com", to, msg)
    print("Msg sent")
    server.quit()


check_price(50000)
# while True:
#     check_price(50000)
#     print("Checking price")
#     time.sleep(60)
