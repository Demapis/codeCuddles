import math

value1 = float(input("value1: "))
results = value1


option_num = int(input("enter number of commands to perform: "))

for _ in range(option_num):

    opinion = int(input('''
    1.add\n2.subtract\n3.divide\n4.multiply\n5.log\n6.sin\n7.cos\n8.sqrt\n9.tan\n'''))    

    if opinion == 1:
        value2 = float(input("value2: "))
        results += value2
        print(f"results = {results}")
    elif opinion == 2:
        value2 = float(input("value2: "))
        results -= value2
        print(f"results = {results}")
    elif opinion == 3:
        value2 = float(input("value2: "))
        results /= value2
        print(f"results = {results}")
    elif opinion == 4:
        value2 = float(input("value2: "))
        results *= value2
        print(f"results = {results}")
    elif opinion == 5:
        results = math.radians(math.log(results))
        print(results )
    elif opinion == 6:
        results = math.radians(math.sin(results))
        print(results )
    elif opinion == 7:
        results = math.radians(math.cos(results))
        print(results )
    elif opinion == 8:
        results = math.radians(math.sqrt(results))
        print(results )
    elif opinion == 9:
        results = math.radians(math.tan(results))
        print(results )
