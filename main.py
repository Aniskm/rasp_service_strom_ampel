import requests
import time

RED_LED_PIN = 17
YELLOW_LED_PIN = 27
GREEN_LED_PIN = 22



def get_energy_data():
    url = "https://www.energy-charts.info/charts/consumption_advice/data/de/day_2024_10_10.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def determine_traffic_light(data):
    current_unix_time = int(time.time()*1000)
    current_unix_time= (current_unix_time // 60000) * 60000
    print(current_unix_time)
  
  
    
    time_list = data[0]['xAxisValues']  

 
    index = time_list.index(current_unix_time)  
    print(index)
    current_value = data[0]['data'][index]  
    print(current_value)
    current_value = data[1]['data'][index]
    print(current_value)
    current_value = data[1]['data'][index-1]
    print(current_value)
   
    
    
    


try:
    while True:
        energy_data = get_energy_data()
        if energy_data:
            determine_traffic_light(energy_data)
        time.sleep(3600)  
finally:
    print("fertig")
