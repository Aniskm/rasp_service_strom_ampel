
import RPi.GPIO as GPIO
import requests
import time
import datetime

# GPIO-Pin-Nummern
RED_LED_PIN = 16
YELLOW_LED_PIN = 20
GREEN_LED_PIN = 21
# clean
GPIO.setwarnings(False)
GPIO.cleanup()
# GPIO-Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

# HTTP-Konstanten
HTTP_OK = 200
previous_led_status = None

def get_date_today():
    current_date = datetime.date.today()
    year = current_date.year
    month = f"{current_date.month:02d}"
    day = f"{current_date.day:02d}"
    return (year, month, day)

def get_energy_data():
    year, month, day = get_date_today()
    print(f"Das heutige Datum: Jahr {year}, Monat {month}, Tag {day}")
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

def find_and_print_data(data, language, key):
    for entry in data:
        if 'name' in entry and language in entry['name'] and entry['name'][language] == key:
            return entry['data']
    print(f"'{key}' in {language} nicht gefunden.")
    return None

def get_current_value(data):
    current_unix_time = int(time.time() * 1000)
    current_unix_time = (current_unix_time // 60000) * 60000
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
        print(f"Der aktuelle Wert ist {current_value}")
        return (current_value, durchschnitt_plus_10[index], durchschnitt_minus_10[index])
    elif renewable_share_of_load_forecast and renewable_share_of_load_forecast[index] is not None:
        current_value = renewable_share_of_load_forecast[index]
        print(f"Der prognostizierte Wert ist {current_value}")
        return (current_value, durchschnitt_plus_10[index], durchschnitt_minus_10[index])
    else:
        print("Keine Daten für die aktuelle Zeit verfügbar.")
        return None

def turn_on_the_led(value_tuple):
    global previous_led_status
    # Schalte alle LEDs aus
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    if not value_tuple:
        print("LED Status: Grau (alle an) => Tuple problem")
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        return

    current_value, upper_limit, lower_limit= value_tuple
    hysteresis = 1
    if previous_led_status == "Grün":
        # Wechsel zu Gelb, wenn current_value < upper_limit - hysteresis
        if current_value < upper_limit - hysteresis:      
            print("LED Status: Gelb")
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
            previous_led_status = "Gelb"
        else:
            print("LED Status: Grün")
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            previous_led_status = "Grün"
    elif previous_led_status == "Gelb":
        if current_value >= upper_limit + hysteresis:
            print("LED Status: Grün")
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            previous_led_status = "Grün"
        elif current_value < lower_limit - hysteresis:
            print("LED Status: Rot")
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
            previous_led_status = "Rot"
        else:
            print("LED Status: Gelb")
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
            previous_led_status = "Gelb"
    elif previous_led_status == "Rot":
        # Wechsel zu Gelb, wenn current_value > lower_limit + hysteresis
        if current_value > lower_limit + hysteresis:
            print("LED Status: Gelb")
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
            previous_led_status = "Gelb"
        else:
            print("LED Status: Rot")
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
            previous_led_status = "Rot"
    elif previous_led_status is None:
        if current_value >= upper_limit + hysteresis:
            print("LED Status: Grün")
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            previous_led_status = "Grün"
        elif current_value < lower_limit - hysteresis:
            print("LED Status: Rot")
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
            previous_led_status = "Rot"
        elif current_value > lower_limit + hysteresis:
            print("LED Status: Gelb")
            GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
            previous_led_status = "Gelb"
         
    else:
        #unerwartete Zustände
        print("Problem bei der Bestimmung des LED-Status.")
        print("LED Status: Grau (alle an)")
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        previous_led_status = None

try:

    energy_data = get_energy_data()
    if energy_data:
        turn_on_the_led(get_current_value(energy_data))



except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    GPIO.cleanup()
