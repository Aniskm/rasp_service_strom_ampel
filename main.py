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
    print(" das heutige datum year {}, monat {},  tag {} ".format(year,month,day))
    url = f"https://www.energy-charts.info/charts/consumption_advice/data/de/day_{year}_{month}_{day}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_data_limit (data,index):
    upper_limit= data[2]['data'][index]
    upper_limit= data[4]['data'][index]

def find_and_print_data(data, language, key):
    for entry in data:
        if 'name' in entry and language in entry['name'] and entry['name'][language] == key:
            return entry['data']
    print(f"'{key}' in {language} not found.")
    return None

def get_current_value (data):
    current_unix_time = int(time.time()*1000)
    current_unix_time= (current_unix_time // 60000) * 60000    
    time_list = data[0]['xAxisValues']  
    index = time_list.index(current_unix_time)  
    
    renewable_share_of_load = find_and_print_data(data, "de", "Anteil EE an Last")
    renewable_share_of_load_forecast = find_and_print_data(data, "de", "Anteil EE an Last Prognose")
    durchschnitt_plus_10 = find_and_print_data(data, "de", "Durchschnitt + 10 %")
    durchschnitt_minus_10 = find_and_print_data(data, "de", "Durchschnitt - 10 %")
 
    
    if renewable_share_of_load[index]:
        current_value = renewable_share_of_load[index]
        print("the value is {}".format(current_value))
        return (current_value,durchschnitt_plus_10[index],durchschnitt_minus_10[index])
    else:   
        current_value = renewable_share_of_load_forecast[index]
        print("the prognose value is {}".format(current_value))
        return (current_value,durchschnitt_plus_10[index],durchschnitt_minus_10[index])
   
   
  
def turn_on_the_led(value_tuple):
    hysteresis = 1
    current_value = value_tuple[0]
    upper_limit = value_tuple[1]
    lower_limit = value_tuple[2]
    if current_value > upper_limit + hysteresis:
        print("gruen")
    elif  lower_limit + hysteresis <= current_value <= upper_limit - hysteresis:
        print("gelb")
    elif current_value < lower_limit - hysteresis:
        print("rot")
    else :
        print("Problem")
    
    


try:
    energy_data = get_energy_data()
    if energy_data:
        turn_on_the_led(get_current_value(energy_data))
   
finally:
    print("fertig")
