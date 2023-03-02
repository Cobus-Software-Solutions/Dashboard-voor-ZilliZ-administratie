import pandas as pd
import numpy as np
import datetime


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import streamlit as st

from ZilliZ_scraping_functions import *


def return_months_between_dates(start_date, end_date):
    if start_date.month < 10:        
        eerste_maand = [f"0{start_date.month}-{start_date.year}"]
    else:
        eerste_maand = [f"{start_date.month}-{start_date.year}"]
    overige_maanden = pd.date_range(start_date, end_date, freq='MS').strftime("%m-%Y").tolist()
    
    return eerste_maand + overige_maanden

def haal_alle_maanden_uit_ZilliZ(driver, datums):
    dfs = []
    for datum in datums:
        try:    
            dfs.append(haal_uren_per_maand_uit_ZilliZ(driver, datum))
        except Exception as e: 
            st.write(e)
            st.warning(f"Voor periode {datum} zijn geen uren geschreven")
    
    return pd.concat(dfs)


def scrape_ZilliZ(user_name, password, start_date, end_date):    
    # Login to Twitter using Selenium
    driver = login(user_name, password)
    
    datums = return_months_between_dates(start_date, end_date)
    df = haal_alle_maanden_uit_ZilliZ(driver, datums)

    # filter op de geselecteerde data
    df = df[(df["datum"] >= pd.to_datetime(start_date)) & (df["datum"] <= pd.to_datetime(end_date))]
    return df
    # df.to_csv("df.csv")

# interessante_kolommen = [
#   "naam",
#   "uur",
#   "datum",
#   "dienst",
#   "omschrijving",
#   "jaar",
#   "maand",
#   "week",
#   "dag",
#   "naam_van_dag"
# ]

st.header("Uren overzicht voor ZilliZ")
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

st.subheader("1. Selecteer de data")
date1, date2 = st.columns(2)

start_date = date1.date_input('Start datum (YYYY/MM/DD)', today)
end_date = date2.date_input('Eind datum (YYYY/MM/DD)', tomorrow)

if start_date > end_date:
    st.error('Error: Eind datum moet later zijn dan start datum.')
    

else:    
    st.subheader("2. Vul je inloggegevens voor ZilliZ in")
    login1, login2 = st.columns(2)
    user_name = login1.text_input("ZilliZ gebruikersnaam", value="")
    password = login2.text_input("ZilliZ wachtwoord", value="")
    
    is_button_clicked =  st.button('Haal informatie op')
     
        
if is_button_clicked:
    df = scrape_ZilliZ(user_name, password, start_date, end_date)
    # df = pd.read_csv("df.csv")
    
    st.subheader("Hoeveel uur heeft iedereen gewerkt?")
    st.write(f"*In de periode van {start_date.day}-{start_date.month}-{start_date.year} tot {end_date.day}-{end_date.month}-{end_date.year}")
    
    
    werknemers_select = st.multiselect("Naar welke werknemers wil je kijken?",
                   set(df["naam"]),
                   set(df["naam"]))
    
    totalen_pivot = df[df["naam"].isin(werknemers_select)].pivot_table("uur", "naam", aggfunc=np.sum)
    st.bar_chart(totalen_pivot, height=600)
    
    
    
    st.subheader("3. Waar spendeert iemand tijd aan?")
    
    col1, col2 = st.columns(2)
    
    werknemer = col1.selectbox("Naar welke werknemer wil je kijken?",
                   list(set(df["naam"])))
    col1.write(werknemer)
    
    Kolom_select = col2.selectbox("Naar welke gegevens wil je kijken?",
                                  list(df.columns.values))
                                # [col for col in df.columns if col not in ["naam", "uur", "comp. uren", "toeslag (uur)"]])
    col2.write(Kolom_select)
    
    werknemer_pivot = df[df["naam"] == werknemer].pivot_table("uur", Kolom_select, aggfunc=np.sum)
    
    st.bar_chart(werknemer_pivot, height=600)
