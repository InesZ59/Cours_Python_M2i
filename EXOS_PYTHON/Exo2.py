print("1.café 1€ \n 2.thé 5€ \n 3.jus 6€ \n 4.sandwich 10€  \n 5.croissant 2€ \n 6.pâtes 12€")


choix_utilisateur = input("choisissez une boisson ou de la nourriture: ")

match choix_utilisateur:
    case "1":
        print(" vous avez choisi un café à 1€")
    case "2":
        print(" vous avez choisi un thé à 5€")                
    case "3":
        print(" vous avez choisi un jus à 6€")    
    case "4":
        print(" vous avez choisi un sandwich à 10€")    
    case "5":
        print(" vous avez choisi un croissaant à 2€")    
    case "6":
        print(" vous avez choisi des pâtes à 12€")