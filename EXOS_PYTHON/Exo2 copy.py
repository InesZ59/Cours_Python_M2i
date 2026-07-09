print("1.café 1€ \n 2.thé 5€ \n 3.jus 6€ \n 4.sandwich 10€  \n 5.croissant 2€ \n 6.pâtes 12€")

choix_utilisateur = input("choisissez une boisson ou de la nourriture: ")

depense = 0

if choix_utilisateur == "1" :
    print("vous avez choisi le café à 1€")
    depense = 1
elif choix_utilisateur == "2" :
    print("vous avez choisi le thé à 5€")
    depense = 5
elif choix_utilisateur == "3" :
    print("vous avez choisi le jus à 6€")
    depense = 6
elif choix_utilisateur == "4" :
    print("vous avez choisi le sandwich à 10€")
    depense = 10
elif choix_utilisateur == "5" :
    print("vous avez choisi le croissant à 2€")
    depense = 2
elif choix_utilisateur == "6" :
    print("vous avez choisi les pâtes à 12€")
    depense = 12       


credit = int(input("vous avez mis :  "))

total = credit - depense
print(total)

