print("===PROGRAMME_NOTES===")
#créer une liste de notes
liste_notes = []
#ajouter une note 
new_note = ""
while new_note != "STOP" :
    new_note = int(input("ajouter une note:"))
    liste_notes.append(new_note)
    print(liste_notes)
    note_max = max(liste_notes)
    print(f"La note maximale est {note_max}")
    note_min = min(liste_notes)
    print(f"La note minimale est {note_min}")
    somme = sum(liste_notes)
    moyenne = somme / len(liste_notes)
    print(f"La moyenne est de {moyenne}")
    if  new_note == 0 :
        print("stop")
        break

