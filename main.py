import requests
import time
import datetime

RED_LED_PIN = 17
YELLOW_LED_PIN = 27
GREEN_LED_PIN = 22


def get_date_today():
    current_date = datetime.date.today()
    year = current_date.year
    month = f"{current_date.month:02d}"  
    day = f"{current_date.day:02d}"      
    return (year,month,day)


def get_energy_data():
    year, month, day = get_date_today()
    print(" der heutige datum year {}, monat {},  tag {} ".format(year,month,day))
    url = f"https://www.energy-charts.info/charts/consumption_advice/data/de/day_{year}_{month}_{day}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_current_value (data):
    current_unix_time = int(time.time()*1000)
    current_unix_time= (current_unix_time // 60000) * 60000    
    time_list = data[0]['xAxisValues']  
    index = time_list.index(current_unix_time)  
    
    if data[0]['data'][index]:
        current_value = data[0]['data'][index]
        print(current_value)
        return current_value
    else:   
        current_value = data[1]['data'][index]
        print(current_value)
        return current_value
   
   
   
    
    
    


try:
    while True:
        energy_data = get_energy_data()
        if energy_data:
            get_current_value(energy_data)
        time.sleep(3600)  
finally:
    print("fertig")
