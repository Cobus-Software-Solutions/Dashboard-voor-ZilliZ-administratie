import pandas as pd
import datetime


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import streamlit as st




today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

start_date = st.date_input('Start date', today)
end_date = st.date_input('End date', tomorrow)

if start_date < end_date:
    st.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
else:
    st.error('Error: End date must fall after start date.')

def login(user_name, password):
    """Functie voor het inloggen bij ZilliZ en het creeren van een chrome driver.

    Args:
        user_name (str): _description_
        password (str): _description_
    """
    #Create a Chrome driver
    driver = webdriver.Chrome()
    driver.get("https://host.landmerc.nl/zilliz/")
    
    #Use the data to login
    element = driver.find_element(By.ID,"aus_username")
    element.send_keys(user_name)
    element = driver.find_element(By.ID,"aus_password")
    element.send_keys(password)
    
    # Log in bij ZilliZ
    element.send_keys(Keys.RETURN)
    
    return driver

def verwerk_maandoverzicht_tabellen(headers, bodies):
    
    tables = []
    for i in range(len(headers)):        
        thead = "<thead>" + headers[i].get_attribute('innerHTML') + "</thead>"
        tbody = "<tbody>" + bodies[i].get_attribute('innerHTML') + "</tbody>"
        table = "<table>" + thead + tbody + "</table>"
        tables.append(" ".join(table.split()))
        
    dfs = [pd.read_html(table)[0] for table in tables]
    for i in range(len(dfs)):
        dfs[i] = dfs[i].iloc[0:-1]
        dfs[i]["naam"] = dfs[i].columns[0]
        dfs[i] = dfs[i].rename(columns={dfs[i].columns[0]: "week"})  
        # st.write(df)
    st.write(dfs[0])
    # st.write(dfs[0].iloc[0:-1])
    # for df in dfs:
    #     st.write(df)
    # st.write(pd.concat(dfs))
    return
    
def uren_per_maand(driver, maand_jaar):
    """Ga naar het maandoverzicht van de administratie en haal alle uren gegevens op per werknemer.

    Args:
        driver (webdriver.Chrome): _description_
        maand (str): MM-YYYY
    """
    # Ga naar het maandoverzicht
    driver.get("https://host.landmerc.nl/applicatie/index.cfm?fuseaction=beheer_administratie.maandstaat_overzicht")
    
    # click op "maandstaat per medewerker"
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/section[1]/form/div[1]/div[2]/div/div/div[1]").click()
    
    # selecteer alle werknemers
    driver.find_element(By.XPATH, "//div[@class='dropdown bootstrap-select show-tick form-control zil-selectie d-print-none']").click()
    driver.find_element(By.XPATH, "//button[@class='actions-btn bs-select-all btn btn-light']").click()
    
    # klik op maand dropdown en selecteer de juist maand
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/section[1]/form/div[1]/div[1]/div[1]/div/div[1]/button").click()
    driver.find_element(By.XPATH, f"//span[text()='{maand_jaar}']").click()
    
    # toon overzicht van de maand
    formulier_element = driver.find_element(By.XPATH, "//div[@class='formulier_knoppen']")
    formulier_element.find_element(By.XPATH, ".//*").click()
    
    # lees de tabel uit
    tables_elements = driver.find_element(By.XPATH, "//table")
    headers = tables_elements.find_elements(By.XPATH, "//thead")
    bodies = tables_elements.find_elements(By.XPATH, "//tbody")

    df = verwerk_maandoverzicht_tabellen(headers, bodies)
    

def scrape_ZilliZ():    
    #Login to Twitter using Selenium
    
    #Data needed to login
    user_name = "testvast"
    password = "Testvast1!"
    
    driver = login(user_name, password)
    
    uren_per_maand(driver, "02-2023")

if st.button('Start scraping ZilliZ') or True:
    result = 1 + 2
    st.write('result: %s' % result)
    scrape_ZilliZ()