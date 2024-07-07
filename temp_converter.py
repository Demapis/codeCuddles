def degree_to_kelvins(temp):
    tempk = temp + 273.25
    return tempk

def kelvins_to_degrees(temp):
    tempc = temp - 273.25
    return tempc

def degrees_to_fahrenheit(temp):
    tempf = (temp * 1.8) + 32
    return tempf

def kelvins_to_fahrenheit(temp):
    tempc = kelvins_to_degrees(temp)
    tempf = degrees_to_fahrenheit(tempc)
    return tempf

def fahrenheit_to_degrees(temp):
    tempc = (temp * 1.8) - 32
    return tempc

def fahreheit_to_kelvins(temp):
    tempc = fahrenheit_to_degrees(temp)
    tempf = degree_to_kelvins(tempc)
    return tempf

def temperature():
        while True:
            try:
                temp = float(input("What's the temperature? "))

                current_units = input("Enter units for temperature ('K' for Kelvins and 'C' for degrees celcius and 'F' for Fahrenheit): ").upper()
                units_to = input("Enter units you want to convert to: ").upper()

                if current_units == "C" and  units_to == "K":
                    print(f"It's {degree_to_kelvins(temp):.2f} kelvins")
                    break
                elif current_units == "K" and units_to == "C":
                    print(f"It's {kelvins_to_degrees(temp):.2f} degrees celcius")   
                    break
                elif current_units == "C" and units_to == "F":
                    print(f"It's {degrees_to_fahrenheit(temp):.2f} fahrenheit")
                    break
                elif current_units == "K" and units_to == "F":
                    print(f"It's {kelvins_to_fahrenheit(temp):.2f} fahrenheit")
                    break
                elif current_units == "F" and units_to == "C":
                    print(f"It's {fahrenheit_to_degrees(temp):.2f} degrees celcisus")
                    break
                elif current_units == "F" and units_to == "K":
                    print(f"It's {fahreheit_to_kelvins(temp):.2f} kelvins")
                    break
                else:
                    print("Invalid units")
                    break
            except ValueError:
                print("Please enter values for temperature")
            
temperature ()
