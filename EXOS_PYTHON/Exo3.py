nombre_joueur1 = input("choisissez un nombre entre 1 et 100: ")

nombre_joueur2 = input("Essaie de trouver le nombre du joueur 1: ")

while nombre_joueur2 != nombre_joueur1:
    
    if nombre_joueur2 > nombre_joueur1 : 
        print("nombre trop HAUT")
    elif nombre_joueur2 < nombre_joueur1 :
        print("nombre trop BAS")
    else :
        print("felicitation")

    nombre_joueur2 = input("Essaie de trouver le nombre du joueur 1: ")

print("Félicitation")
