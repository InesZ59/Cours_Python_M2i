#trouvez un numero entre 0 et 100
numero_mystere = input("Veuillez choisir un numéro entre 0 et 100: ")
numero_test = input("le numero que je choisis est: ")
#faire condition si numero trop bas ou trop haut 
while True :
    if numero_test < numero_mystere :
        print("TROP BAS")
        numero_test = input("Veuillez choisir un numéro entre 0 et 100: ")
    elif numero_test > numero_mystere :
        print("TROP HAUT")
        numero_test = input("Veuillez choisir un numéro entre 0 et 100: ") 
    else :
        print("FELICITATION") 
        break 
            
  