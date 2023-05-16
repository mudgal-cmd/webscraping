from selenium import webdriver
# imported the 'By' module that will help us in interacting with the HTML elements along with Selenium
from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
import re
import pandas as pd
import os
# import pathlib
import sqlite3 as sql

# created a chromedriver instance
driver = webdriver.Chrome("chromedriver")
# loading the URL.
driver.get("https://finance.yahoo.com/trending-tickers")
# this element is the 'Next'/'Previous' button (arrow) to load the next set of commodities.
element = driver.find_element(By.XPATH, '//*[@id="market-summary"]/div/div[1]/div[2]/button[2]')
data_lst = []
# DATA RETRIEVAL

# We want the program to click the button until we reach the end/button is not clickable anymore.
for no_of_clicks in range(0, 4):
    # All the commodities are defined under a parent div element, and we're storing
    # that same div element's info inside 'div_element' variable.
    # Interacting with the div element using the unique XML PATH extracted using the chrome/browser dev tools
    div_element = driver.find_element(By.XPATH, '//*[@id="market-summary"]/div/div[1]/div[1]/ul')
    # print(div.text)
    # appending all the text info (commodities info) inside the div_element in the 'data_lst'
    data_lst.append(div_element.text)
    # navigating to the end of the commodities list
    element.click()

    # DATA CLEANSING

# print(data_lst)
temp = []
d = ""
# created a string ('d') out of the data list which is formed in such a way that every
# piece of text is separated by a newline
for items in data_lst:
    d = d + items
# splitting the string so that we get every text as a separate element in the list
temp = d.split("\n")
# Since we do not need the amount of profit or loss, hence to remove it from the string,
# a variable 'profit_or_loss' is created which will be removed eventually from the list.
profit_or_loss = [i for i in temp if (i.startswith("+") or i.startswith("-"))]
print(f": {profit_or_loss}")
# final list contains the name of the commodity along with the price, but some values are repeated,
# because we navigated to each and every section on the yahoo ticker's page and the commodity info
# was being repeated in the following sections.
final = [i for i in temp if i not in profit_or_loss]
# print(f"Cleaned list: {final}")
cleaned_list = []
for i in final:
    if i not in cleaned_list:
        cleaned_list.append(i)
# 'cleaned_list' as the name suggests, contains the cleaned version of the
# information - without duplicates, without irrelevant info (profit or loss percentage).
print(f"Final : {cleaned_list}")
# Finally, 'commodities' list contains the information of the commodities that we need for our project.
commodities = []
for i in range(0, len(cleaned_list) - 1, 2):
    if (cleaned_list[i] == "Crude Oil") or (cleaned_list[i] == "Gold") or (cleaned_list[i] == "Silver"):
        # Since, some prices contain ',' (that makes them a string) which cannot be converted directly
        # to float,hence removed the comma (using regex) to make it as a float element.
        commodities.append([cleaned_list[i], re.sub("[,]", "", cleaned_list[i + 1])])
print(f"The resulting data to be stored in the txt file and db is\n: {commodities}")

# STORING THE REQUIRED DATA

# created a dataframe that holds the relevant commodities
df = pd.DataFrame(commodities, columns=["TICKER", "PRICE"])
txt_file = "commodity_prices.txt"
# checking if the txt file exists in the directory, if yes, then os.remove() will delete the file.
if os.path.exists(txt_file):
    os.remove(txt_file)

# writing the commodity details in the text file
with open(txt_file, "x") as file:
    dftoString = df.to_string(header=True, index=True)
    for content in dftoString:
        file.writelines(content)

        # DATABASE FUNCTIONALITY

# checking if the Commodity DB file exists, if it does, we will remove the file
if os.path.exists("CommodityDatabase.db"):
    os.remove("CommodityDatabase.db")
# name of the db file
db_file = "CommodityDatabase.db"
# opened a connection to the database
connection = sql.connect(db_file)
# created a cursor to execute the queries.
cursor = connection.cursor()
# table created
cursor.execute("CREATE Table CommodityTable (TICKER VARCHAR2, PRICE REAL)")
# inserting the values (nested list) in the CommodityTable
for i in commodities:
    cursor.execute("INSERT into CommodityTable values(?,?)", i)

# querying the CommodityTable in the CommodityDatabase
res = cursor.execute("SELECT * from CommodityTable")

print(f"Selecting all the data from the commodity table produces below result\n: {res.fetchall()}")
connection.close()