import requests
import time
import datetime
from gpiozero import LED

HTTP_OK = 200
RED_LED_PIN = "GPIO16" 
YELLOW_LED_PIN = "GPIO20" 
GREEN_LED_PIN = "GPIO21"

red_led = LED(RED_LED_PIN)
yellow_led = LED(YELLOW_LED_PIN)
green_led = LED(GREEN_LED_PIN)

def get_date_today():
    current_date = datetime.date.today()
    year = current_date.year
    month = f"{current_date.month:02d}"  
    day = f"{current_date.day:02d}"      
    return (year, month, day)


def get_energy_data():
    year, month, day = get_date_today()
    print(" das heutige datum year {}, monat {},  tag {} ".format(year,month,day))
    url = f"https://www.energy-charts.info/charts/consumption_advice/data/de/day_{year}_{month}_{day}.json"
    retries = 5
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == HTTP_OK:
                return response.json()
            else:
                print(f"Fehler beim Abrufen der Daten, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der Daten: {e}")
        time.sleep(5)  
    print("Konnte die Daten nach mehreren Versuchen nicht abrufen.")
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
    try:
        index = time_list.index(current_unix_time)
    except ValueError:
        print("Aktuelle Zeit nicht in xAxisValues gefunden.")
        return None
    
    renewable_share_of_load = find_and_print_data(data, "de", "Anteil EE an Last")
    renewable_share_of_load_forecast = find_and_print_data(data, "de", "Anteil EE an Last Prognose")
    durchschnitt_plus_10 = find_and_print_data(data, "de", "Durchschnitt + 10 %")
    durchschnitt_minus_10 = find_and_print_data(data, "de", "Durchschnitt - 10 %")
    
    if not durchschnitt_plus_10 or not durchschnitt_minus_10:
        print("Durchschnittsdaten nicht gefunden.")
        return None
    
    if renewable_share_of_load and renewable_share_of_load[index] is not None:
        current_value = renewable_share_of_load[index]
        print("the value is {}".format(current_value))
        return (current_value,durchschnitt_plus_10[index],durchschnitt_minus_10[index])
    elif renewable_share_of_load_forecast and renewable_share_of_load_forecast[index] is not None:  
        current_value = renewable_share_of_load_forecast[index]
        print("the prognose value is {}".format(current_value))
        return (current_value,durchschnitt_plus_10[index],durchschnitt_minus_10[index])
    else:
        print("Keine Daten für die aktuelle Zeit verfügbar.")
        return None
   
  
def turn_on_the_led(value_tuple):
    hysteresis = 1
    if not value_tuple:
        print("grau")
        red_led.on()
        yellow_led.on()
        green_led.on()
        return
    current_value, upper_limit, lower_limit = value_tuple

    if current_value > upper_limit + hysteresis:
        print("gruen")
        green_led.on()
    elif  lower_limit + hysteresis <= current_value <= upper_limit - hysteresis:
        print("gelb")
        yellow_led.on()
    elif current_value < lower_limit - hysteresis:
        print("rot")
        red_led.on()
    else :
        print("Problem bei der Bestimmung des LED-Status.")
        print("grau")
        red_led.on()
        yellow_led.on()
        green_led.on()
    
    


try:
    energy_data = get_energy_data()
    if energy_data:
        turn_on_the_led(get_current_value(energy_data))

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    print("grau")
    red_led.on()
    yellow_led.on()
    green_led.on()
   
finally:
    print("fertig")
