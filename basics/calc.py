import math

def float_input():
    while True:
        try:        
            value1 = float(input("value1: "))
            results = value1


            option_num = int(input("enter number of commands to perform: "))

            for _ in range(option_num):
                option = int(input('''Choose an operation:\n1.add\n2.subtract\n3.divide\n4.multiply\n5.log\n6.sin\n7.cos\n8.sqrt\n9.tan\nEnter a number corresponding to the operation: '''))    

                if option in [1,2,3,4]:
                    value2 = float(input("Enter value2: "))
                    if option == 1:
                        results += value2
                    elif option == 2:
                        results -= value2
                    elif option == 3:
                        if value2  == 0:
                            print("Division by zero error")
                            continue
                        else:
                            results /= value2
                    elif option == 4:
                        results *= value2
                elif option == 5:
                    if results < 0:
                        print("Can find logs of only positive numbers.")
                        continue
                    results =math.log(results)
                    print(results )
                elif option == 6:
                    results = math.sin(math.radians(results))
                    print(results )
                elif option == 7:
                    results = math.cos(math.radians(results))
                    print(results )
                elif option == 8:
                    if results < 0:
                        print("Can't find qrt of negative values.")
                        continue
                    results =math.sqrt(results)
                    print(results )
                elif option == 9:
                    results = math.tan(math.radians(results))
                    print(results)
                else:
                    print("Invalid option")
                print(f"Results = {results:.4f}")

                
            continuation = input("Do you want to continue? Y/N ").lower()
            if continuation != "y":
                print(f"Results = {results:.4f}")
                break
            else:
                value1 = results
                
        except ValueError:
            print("Use values and not strings for calculations!")


float_input ()
            
