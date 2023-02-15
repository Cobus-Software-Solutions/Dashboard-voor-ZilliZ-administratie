import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TO DO: wat gebeurt er als het verkeerde wachtwoord is gebruikt?
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

def verwerk_maandoverzicht_tabellen(headers, bodies, maand_jaar):
    """Verwerk de selenium elements en zet ze om naar een Pandas DataFrame

    Args:
        headers (selenium.webdriver.remote.webelement.WebElement): Selenium header element van een HTML tabel
        bodies (selenium.webdriver.remote.webelement.WebElement): Selenium body element van een HTML tabel
        maand_jaar (str): string met de maand en het jaar

    Returns:
        pandas.DataFrame: Een Pandas DataFrame met daarin alle uren van 1 maand
    """
    
    # verander alle elements naar html
    tables = []
    for i in range(len(headers)):        
        thead = "<thead>" + headers[i].get_attribute('innerHTML') + "</thead>"
        tbody = "<tbody>" + bodies[i].get_attribute('innerHTML') + "</tbody>"
        table = "<table>" + thead + tbody + "</table>"
        tables.append(" ".join(table.split()))
    
    # en sla ze op als pandas dataframe        
    dfs = [pd.read_html(table)[0] for table in tables]
    
    # bewerk nu elke dataframe
    for i in range(len(dfs)):
        dfs[i] = dfs[i].iloc[0:-1]      # verwijder laatste rij
        dfs[i]["naam"] = dfs[i].columns[0]      # voeg de naam van de persoon toe aan elke rij
        dfs[i] = dfs[i].rename(columns={dfs[i].columns[0]: "week"})                                 # geef de kolom voor de weken de juiste naam
        dfs[i] = dfs[i][ ['naam'] + [ col for col in dfs[i].columns if col != 'naam' ] ]
        dfs[i]["week"] = dfs[i]["week"].ffill()                                                     # forward fill de weken
        dfs[i]["uur"] = dfs[i]["uur"] / 100                                                         # uren werden als duizenden opgeslagen dus verander die naar normale uren
        
        # datum dingetjes
        dfs[i] = dfs[i].rename(columns={"dag": "naam_van_dag"})
        dfs[i]["datum"] = dfs[i]["datum"].apply(lambda x: str(x)+ "-" + maand_jaar.split("-")[1])   # Voeg nog het jaartal toe
        dfs[i]["datum"] = pd.to_datetime(dfs[i]["datum"], dayfirst=True)   
        dfs[i]["jaar"] = dfs[i]["datum"].dt.year
        dfs[i]["maand"] = dfs[i]["datum"].dt.month
        dfs[i]["dag"] = dfs[i]["datum"].dt.day
        
    return pd.concat(dfs)
    
def haal_uren_per_maand_uit_ZilliZ(driver, maand_jaar):
    """Ga naar het maandoverzicht van de administratie en haal alle uren gegevens op per werknemer.

    Args:
        driver (webdriver.Chrome): _description_
        maand_jaar (str): MM-YYYY
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

    return verwerk_maandoverzicht_tabellen(headers, bodies, maand_jaar)