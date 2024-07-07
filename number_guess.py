import random

# max_guesses = 3
# attempts =int(input("How many times do you want to attempt? "))
range_guess = int(input("""choose your suitable guess range\n1. Easy (range from 0 to 50) \n2. Medium (range from 0 to 100) \n3. range (range from 0 to 200)\n: """))

def guess():             
        while  True:
            try: 

                    
                    if range_guess == 1:
                        comp_guess = random.randint(0,50)
                        attempts = 6
                        scores = attempts 
                        for i in range(attempts):
                            player_guess = int(input("Player guess: "))
                            scores -= 1                               
                            if comp_guess > player_guess:
                                print("your guess a little bit lower. Try again!: ")
                            elif comp_guess < player_guess:
                                print("your guess a little higher. Try again!: ")
                            
                            elif comp_guess == player_guess:
                                print("you won!")
                                break
                    elif range_guess == 2:
                        comp_guess = random.randint(0,100)
                        attempts = 15
                        scores = attempts 
                        for i in range(attempts):
                            player_guess = int(input("Player guess: "))
                            scores -= 1                               
                            if comp_guess > player_guess:
                                print("your guess a little bit lower. Try again!: ")
                            elif comp_guess < player_guess:
                                print("your guess a little higher. Try again!: ")
                            
                            elif comp_guess == player_guess:
                                print("you won!")
                                break
                    elif range_guess == 3:
                        comp_guess = random.randint(0,200)
                        attempts = 30
                        scores = attempts 
                        for i in range(attempts):
                            player_guess = int(input("Player guess: "))
                            scores -= 1                               
                            if comp_guess > player_guess:
                                print("your guess a little bit lower. Try again!: ")
                            elif comp_guess < player_guess:
                                print("your guess a little higher. Try again!: ")
                            
                            elif comp_guess == player_guess:
                                print("you won!")
                                break
                    else:
                         print("Your opinion is out of range.")
                         scores = 0
                                
                            
                    print(scores ,"= your scores")
                                
            except ValueError:
                print("guess digit values")
                              
                              
                        
guess()

# # how many times you want to attempt
# # the range of your guess
# # display remaining atempts
# # want to play the game again
# # used any other  data type(error)
# # how far is your guess from the answer

# # produce sounds for right and wrong
# # provide a hint
# # save and load game state


# import random

# comp = random.randint(0,9)
# attempts = 6
# scores = attempts
# for i in range(attempts):
#     player = int(input("Player: "))
#     if player == comp:
#         print("you won!")
#         break
#     elif player != comp:
#         print("try again: ")