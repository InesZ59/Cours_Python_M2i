#créer une balle
la_balle = "place_balle"
#créer 5 gobelets
bonneteau = ["1", "2", "3", "4", "5"]

#positionner la balle dans un gobelet
import random
place_balle = random.randint(0,6)

choix_balle = int(input("Choisir un gobelet: "))

if place_balle != choix_balle :
        print(input(f"La balle se trouve dans le {place_balle}"))
else :
        print("FELICITATION, vous avez gagné")


