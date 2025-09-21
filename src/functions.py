import requests
from datetime import datetime, timedelta, date

STATION_NAME = ["Lille", "Lorient", "Paris Gare du Nord", "Paris Montparnasse", "Rennes", "Lyon Part-Dieu", "Paris Gare de Lyon"]
STATION_CODE = {"Lorient": "FRLRT", "Rennes": "FRRNS", "Paris Montparnasse": "FRPMO", "Paris Gare du Nord": "FRPNO", "Lille": "FRADJ", "Lyon Part-Dieu": "FRLPD", "Paris Gare de Lyon":"FRPLY"}
TIME_DELTA = 60

def getDbStatus():
    
    yesterday = date.today() - timedelta(days=1)
    formated_yesterday = yesterday.strftime("%Y-%m-%d")
    url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?limit=100&refine=date%3A" + "\"" + formated_yesterday + "\""
    request = requests.get(url)
    if request.status_code == 200:
        if request.json()["total_count"] == 0:
            return True
        else:
            return False
    else:
        return None

def dateToAPI(date_input):
    
    input_format = "%d %B %Y"
    output_format = "%Y-%m-%d"
    date_datetime = datetime.strptime(date_input, input_format)
    
    return date_datetime.strftime(output_format)

def checkDate(date):
    
    url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?limit=100&refine=date%3A" + "\"" + date + "\""
    request = requests.get(url)
    if request.status_code == 200:
        if request.json()["total_count"] == 0:
            return False, "La date indiqué n'est pas dans la range TGV MAX"
        else:
            return True, ""
    else:
        return False, "Erreur lors du check de la date"

def requestURL(origin, destination, train_date):
    
    prefixe = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?order_by=heure_depart&limit=100"
    url_origin = "&refine=origine_iata%3A" + "\"" + origin + "\""
    url_destination = "&refine=destination_iata%3A" + "\"" + destination + "\""
    url_date = "&refine=date%3A" + "\"" + train_date + "\""
    final_url = prefixe + url_destination + url_origin + url_date
    
    return final_url

def isInTimeRange(time_ref, time):
    
    time_format = "%H:%M"
    ref_datetime = datetime.strptime(time_ref, time_format)
    time_datetime = datetime.strptime(time, time_format)
    
    minus_range = ref_datetime - timedelta(minutes=TIME_DELTA)
    plus_range = ref_datetime + timedelta(minutes=TIME_DELTA)
    
    return minus_range <= time_datetime <= plus_range

def requestTreatment(time_ref, request):
    
    considered_train = []
    data = request.json()["results"]
    for train in data:
        if isInTimeRange(time_ref, train["heure_depart"]):
            considered_train.append(train)
    return considered_train

def getTrains(train):
    train_date = dateToAPI(train["Date"])
    date_ok, message = checkDate(train_date)
    if not date_ok:
        return [], message
    else:
        url = requestURL(STATION_CODE[train["Origine"]], STATION_CODE[train["Destination"]], train_date)
        request = requests.get(url)
        if request.status_code == 200:
            train_list = requestTreatment(train["Heure"], request)
            if train_list:
                return train_list, ""
            else:
                return [], f"Pas de train autour de {train["Heure"]}"
        else:
            return [], "Erreur dans la requete"
    