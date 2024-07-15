def degrees_to_kelvins(temp):
    tempk =temp + 273.15
    return tempk
# ------------------------
def degrees_to_fahrenheit(temp):
    tempf = (temp * 1.8) + 32
    return tempf
# ------------------------
def kelvins_to_degrees(temp):
    tempc = temp - 273.15
    return tempc
# ------------------------
def kelvins_to_fahrenheit(temp):
    tempc = kelvins_to_degrees(temp)
    tempf = degrees_to_fahrenheit(tempc)
    return tempf
# ------------------------
def fahrenheit_to_degrees(temp):
    tempc = (temp -32) / 1.8
    return tempc
# ------------------------
def fahrenheit_to_kelvins(temp):
    tempc = fahrenheit_to_degrees(temp)
    tempk = degrees_to_kelvins(tempc)
    return tempk
# ------------------------
while True:
    try: 
        temperature = input("Ennter the temperature or (type 'exit' to quit): ")
        if temperature.lower() == "exit":
            break
        temp= float(temperature)
        current_units,units_to = input("Choose units for your temperature and units to convert into separating with a space('K' for kelvins 'C' for degrees celcius and 'F' for fahrenheit): ").upper().split()
        conversion_functions = {
            ("C", "K"): degrees_to_kelvins,
            ("C", "F"): degrees_to_fahrenheit,
            ("K", "C"): kelvins_to_degrees,
            ("K", "F"): kelvins_to_fahrenheit,
            ("F", "C"): fahrenheit_to_degrees,
            ("F", "K"): fahrenheit_to_kelvins
        }
        try:
                
            conversion_functions =conversion_functions[(current_units,units_to )]
            converted_temp = conversion_functions(temp)
            print(f"{temp}{current_units} is equivalent to {converted_temp:.2f}{units_to}")
        except ValueError:
            print("Use 'K' ,'C', or 'F' for units")
    except ValueError:
        print("use values for temperature")

