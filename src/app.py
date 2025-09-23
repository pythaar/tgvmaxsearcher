import os
import sys
import json
import requests
import pandas as pd
import streamlit as st
GIT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(GIT_PATH)
from config import APP_PASSWORD
from src.functions import getDbStatus
from src.file_manipulation import openJson, createJsonIfNot
from datetime import datetime, timedelta, date

def devPrint(to_print):
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempLogs.log')
    with open(log_path, 'a') as file:
        file.write(to_print + '\n')
        file.close()
            
def displayRegisteredTrains(train_list, train_to_find_path, apply_btn_state):
    
    if not train_list:
        st.write('Pas de train enregistré')
    else:
        train_df = pd.DataFrame(train_list)
        columns_name = train_df.columns
        train_df["Supprimer"] = False
        updated_train_df = st.data_editor(
                                train_df,
                                column_config={
                                    "Supprimer": st.column_config.CheckboxColumn(
                                        "Supprimer",
                                        help="Supprimer un train",
                                        default=False,
                                    )
                                },
                                disabled=columns_name,
                                hide_index=True,
                            )
        
        
        if st.button('Supprimer', disabled=apply_btn_state):
            trains_to_keep = updated_train_df.index[updated_train_df['Supprimer'] == False].tolist()
            new_train_list = []
            for index_train in trains_to_keep:
                new_train_list.append(train_list[index_train])
                
            with open(train_to_find_path, 'w') as json_file:
                json.dump(new_train_list, json_file)
                
            st.rerun()
            
def convertToDict(origine, destination, date, heure):
    
    strheure = heure.strftime("%H:%M")
    strdate = date.strftime("%d %B %Y")
    trainDict = {"Origine": origine, "Destination": destination, "Date": strdate, "Heure": strheure}

    return trainDict

def addTrain(train_list, json_path, apply_btn_state, station_code):
    
    station_name = list(station_code.keys())
    add_train = st.expander('Ajouter un train')
    origine = add_train.selectbox('Départ', station_name)
    destination = add_train.selectbox('Arrivée', station_name)
    train_date = add_train.date_input('Date', format='DD/MM/YYYY')
    heure = add_train.time_input('Heure')
    if add_train.button('Ajouter', disabled = apply_btn_state):
        new_train_dict = convertToDict(origine, destination, train_date, heure)
        train_list.append(new_train_dict)
        with open(json_path, 'w') as json_file:
            json.dump(train_list, json_file)
        st.rerun()

def dateToAPI(date_input):
    
    input_format = "%d %B %Y"
    output_format = "%Y-%m-%d"
    date_datetime = datetime.strptime(date_input, input_format)
    date_output = date_datetime.strftime(output_format)
    #date_url = date_output[:4] + "%2F" + date_output[5:7] + "%2F" + date_output[8:]
    
    return date_datetime.strftime(output_format)

def requestURL(origin, destination, train_date):
    
    prefixe = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?order_by=heure_depart&limit=100"
    url_origin = "&refine=origine_iata%3A" + "\"" + origin + "\""
    url_destination = "&refine=destination_iata%3A" + "\"" + destination + "\""
    url_date = "&refine=date%3A" + "\"" + train_date + "\""
    final_url = prefixe + url_destination + url_origin + url_date
    
    return final_url

def in30Mins(time_ref, time):
    
    time_format = "%H:%M"
    ref_datetime = datetime.strptime(time_ref, time_format)
    time_datetime = datetime.strptime(time, time_format)
    
    minus_range = ref_datetime - timedelta(minutes=60)
    plus_range = ref_datetime + timedelta(minutes=60)
    
    return minus_range <= time_datetime <= plus_range
  
def requestTreatment(time_ref, request):
    
    considered_train = []
    data = request.json()["results"]
    for train in data:
        if in30Mins(time_ref, train["heure_depart"]):
            considered_train.append(train)
    return considered_train

def colorer_critere(valeur):
    if valeur == "OUI":
        return 'background-color: green'
    elif valeur == "NON":
        return 'background-color: red'
    
def displayTrains(train):
    
    available_train = train["trainList"]
    if available_train == None:
        pass
    elif available_train:
        df_train = pd.DataFrame(train["trainList"])
        df_to_display = df_train[["heure_depart", "heure_arrivee", "od_happy_card"]]
        df_to_display.rename(columns={"od_happy_card": "TGV MAX", "heure_depart": "Heure de départ", "heure_arrivee": "Heure d arrivée"}, inplace=True)
        df_stylise = df_to_display.style.applymap(colorer_critere, subset=['TGV MAX'])
        st.dataframe(df_stylise, hide_index=True)
    else:
        st.warning("No train arround " + train["Heure"])

def checkDate(date):
    
    url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?limit=100&refine=date%3A" + "\"" + date + "\""
    request = requests.get(url)
    if request.status_code == 200:
        if request.json()["total_count"] == 0:
            st.warning("La date indiqué n'est pas dans la range TGV MAX")
            return False
        else:
            return True
    else:
        st.error("Erreur lors du check d'update")
        return False

def checkTrains(train_list, station_code):
    
    for train in train_list:
        st.write("De " + train["Origine"] + " à " + train["Destination"] + ", le " + train["Date"] + ":")
        train_date = dateToAPI(train["Date"])
        date_ok = checkDate(train_date)
        if date_ok:
            url = requestURL(station_code[train["Origine"]], station_code[train["Destination"]], train_date)
            request = requests.get(url)
            if request.status_code == 200:
                train["trainList"] = requestTreatment(train["Heure"], request)
            else:
                train["trainList"] = None
        else:
            train["trainList"] = None
    
        displayTrains(train)

def checkUpdate():
    
    dbStatus = getDbStatus()
    if dbStatus == True:
        st.success("La database est update")
    elif dbStatus == False:
        st.warning("La database n'est pas à jour")
    else:
        st.error("Erreur lors du check d'update") 

def main():
    """Main app function
    """
    #Titles
    st.title('TGV Max Searcher')
    st.subheader('By Jules aka Pytpyt')
    st.divider()
    st.subheader('Liste des trains à chercher')
    
    #Open train to find
    db_path = os.path.join(GIT_PATH, 'database')
    train_to_find_path = os.path.join(db_path, 'trainsToFind.json')
    stationCode_path = os.path.join(db_path, 'stationCode.json')
    createJsonIfNot(train_to_find_path, [])
    train_list = openJson(train_to_find_path)
    station_code = openJson(stationCode_path)
    
    #Check password
    userpasswd = st.text_input('Password', type='password')
    apply_btn_state = not (userpasswd == APP_PASSWORD)
    
    displayRegisteredTrains(train_list, train_to_find_path, apply_btn_state)
    
    addTrain(train_list, train_to_find_path, apply_btn_state, station_code)
    
    if st.button('Check la dispo'):
        checkUpdate()
        checkTrains(train_list, station_code)
        
    st.text('To be done...')
    
    
if __name__ == "__main__":
    main()