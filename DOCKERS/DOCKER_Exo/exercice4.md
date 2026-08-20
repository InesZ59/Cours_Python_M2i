# Exercice

## Partie 1

- En utilisant votre machine Windows, lancez le service Docker, s’il n’est pas lancé.

- Créer une image Docker sur votre machine du jeu 2048 (voir screen jeux_2048).
```bash
docker search 2048
docker pull quchaonet/2048
```
- Vérifier que l’image est bien présente sur votre machine.
```bash
docker images
"quchaonet/2048:latest     b1ced866c7c1       12.2MB          3.7MB"
```
- Lancer ce jeu sur un port disponible au travers d’un conteneur que vous allez appeler «jeu-votre-nom ». 
```bash
docker run -d -p 8083:80 --name jeu1-ines oats87/2048 
```
- Vérifier que le conteneur est bien lancé avec la commande adaptée.
```bash
docker ps
``` 
- Créer un second conteneur qui va lancer le même jeu mais avec un nom différent «jeu2-votre-nom ».
```bash
docker run -d -p 8084:80 --name jeu-zounon oats87/2048
```
- Les 2 jeux sont fonctionnels en même temps sur votre machine, effectuez la commande pour vérifier la présence des conteneurs.
```bash
docker ps
```
- Ouvrez les 2 jeux sur votre navigateur. 
```bash
http://localhost:8084/
http://localhost:8083/
```
- Stopper les 2 conteneurs et assurez-vous que ces 2 conteneurs sont arrêtés.
```bash
docker stop jeu1-ines
docker stop jeu-zounon
```
- Relancez le conteneur «jeu2-votre-nom » et aller vérifier dans votre navigateur s’il fonctionne bien. Effectuez la commande pour voir s’il a bien été relancé. Puis stopper le. 
```bash
docker start jeu-zounon
docker ps 
```
- Supprimez l’image du jeu 2048 et les conteneurs associés.
```bash
docker stop jeu-zounon
docker stop jeu1-ines
docker rm jeu-zounon
docker rm jeu1-ines
docker rmi oats87/2048
```
- Vérifiez que les suppressions ont bien été faite.
```bash
docker ps
```

## Partie 2


- Récupérer une image docker nginx
```bash
docker pull nginx
```
- Créer un conteneur en vous basant sur cette image en lui attribuant le nom suivant : « nginx-web».
```bash
docker run --name nginx-web nginx
```
- Assurez-vous que l’image est bien présente et que le conteneur est bien lancé.
```bash
docker ps -a (mon conteneur est arrêté car j'ai du sortir de la commande suivante)
CONTAINER ID   IMAGE            COMMAND                  CREATED              STATUS                          PORTS                                     NAMES
56312de69957   nginx            "/docker-entrypoint.…"   About a minute ago   Exited (0) About a minute ago                                             nginx-web

docker start nginx-web (pour le relancer)
```
- Ce serveur nginx web (nginx-web) devra être lancé sur un port disponible.

- Vérifier que le serveur est bien lancé au travers du navigateur.

- Une page web avec «Welcome to nignx » devrait s'afficher (voir nginx.png). 

- Effectuer la commande vous permettant de rentrer à l’intérieur de votre serveur nginx.

- Une fois à l’intérieur, aller modifier la page html par défaut de votre serveur nginx en changeant le titre de la page en :  
Welcome «votre prenom ».

- Relancez votre serveur et assurez-vous que le changement à bien été pris en compte, en relançant votre navigateur.

- Refaite la même opération mais en utilisant le serveur web apache et donc il faudra créer un autre conteneur.

- Il faut supprimer le contenu complet de l'index.html et y mettre : "Je suis heureux et je m'appelle votre prenom".

- Le changement doit appaître dans votre navigateur.

## Partie 3


- Répétez 3 fois la même opération que pour le début de la partie 2, il faudra juste appelez vos conteneurs :

- « nginx-web3 ».

- « nginx-web4 ».

- « nginx-web5 ».

- Il faudra faire en sorte que les pages html présente dans les fichiers ci-dessous s’affiche dans chacun des navigateurs en lien avec vos conteneurs :

- html5up-editorial-m2i.zip pour nginx-web3

- html5up-massively.zip pour nginx-web4

- html5up-paradigm-shift.zip pour nginx-web5

- Stopper, ensuite, ces différents conteneurs.
