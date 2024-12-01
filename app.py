import os
import json
import pandas as pd
import streamlit as st

STATION_NAME = ["Lille", "Lorient", "Paris Gare du Nord", "Paris Montparnasse", "Rennes"]

def devPrint(to_print):
    with open('tempLogs.log', 'a') as file:
        file.write(to_print + '\n')
        file.close()

def createJsonIfNot(file_path):
    
    json_dict = [{"Origine": "Gare d origine", "Destination": "Gare d arrivee", "Date": "JJ Month AAAA", "Heure": "HH:MM"}]
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(json_dict, json_file)
            
def displayRegisteredTrains(train_list, json_path):
    
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
        
        
        if st.button('Supprimer'):
            trains_to_keep = updated_train_df.index[updated_train_df['Supprimer'] == False].tolist()
            new_train_list = []
            for index_train in trains_to_keep:
                new_train_list.append(train_list[index_train])
                
            with open(json_path, 'w') as json_file:
                json.dump(new_train_list, json_file)
                
            st.rerun()
            
def convertToDict(origine, destination, date, heure):
    
    strheure = heure.strftime("%H:%M")
    strdate = date.strftime("%d %B %Y")
    trainDict = {"Origine": origine, "Destination": destination, "Date": strdate, "Heure": strheure}

    return trainDict

def addTrain(train_list, json_path):
    
    add_train = st.expander('Ajouter un train')
    origine = add_train.selectbox('Départ', STATION_NAME)
    destination = add_train.selectbox('Arrivée', ("Lille", "Paris Montparnasse", "Paris Gare du Nord", "Lorient", "Rennes"))
    date = add_train.date_input('Date', format='DD/MM/YYYY')
    heure = add_train.time_input('Heure')
    if add_train.button('Ajouter'):
        new_train_dict = convertToDict(origine, destination, date, heure)
        train_list.append(new_train_dict)
        with open(json_path, 'w') as json_file:
            json.dump(train_list, json_file)
        st.rerun()
    
    #with st.form("my_form"):
        
        
        # st.title('Ajouter un train')
        # origine = st.selectbox('Départ', ("Lille", "Paris Montparnasse", "Paris Gare du Nord", "Lorient", "Rennes"))
        # destination = st.selectbox('Arrivée', ("Lille", "Paris Montparnasse", "Paris Gare du Nord", "Lorient", "Rennes"))
        # date = st.date_input('Date', format='DD/MM/YYYY')
        # heure = st.time_input('Heure')
        
        # if st.form_submit_button('Ajouter'):
        #     new_train_dict = convertToDict(origine, destination, date, heure)
        #     train_list.append(new_train_dict)
        #     with open(json_path, 'w') as json_file:
        #         json.dump(train_list, json_file)
        #     st.rerun()
            

def main():
    st.title('TGV Max Searcher')
    st.subheader('By Jules aka Pytpyt')
    st.divider()

    st.subheader('Liste des trains à chercher')
    
    #Make sure json exists
    json_path = 'trainsToFind.json'
    createJsonIfNot(json_path)
    
    with open(json_path, 'r') as json_file:
        input_json = json.load(json_file)
        
    displayRegisteredTrains(input_json, json_path)
    
    addTrain(input_json, json_path)
    
    if st.button('Check la dispo'):
        st.warning('GROS RATIO 😭😭😭')
    
    
if __name__ == "__main__":
    main()