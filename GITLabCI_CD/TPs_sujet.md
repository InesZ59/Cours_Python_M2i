# Cahier de TP DevOps

## Mise en contexte

Ce cahier propose une série de travaux pratiques DevOps construits autour d’un même projet.

Les différents TP forment une progression continue : chaque étape reprend le travail réalisé précédemment et ajoute de nouvelles fonctionnalités ou de nouveaux outils.

Il est donc important de réaliser les TP dans l’ordre.

Le TP2 part du résultat obtenu à la fin du TP1, le TP3 reprend le projet après le TP2, et ainsi de suite jusqu’au TP6. Il est donc déconseillé de commencer un TP sans avoir terminé les précédents.

Au fil des différentes étapes, vous serez amené à faire évoluer une application Python, à la conteneuriser, à lui ajouter une base de données, puis à mettre progressivement en place un workflow GitLab et une chaîne d’intégration et de livraison continues.

## Règles de travail

Quelques bonnes pratiques devront être respectées pendant l’ensemble des TP :

1. Chaque étape doit aboutir à un projet fonctionnel avant de passer à la suivante.

2. Les modifications doivent être enregistrées régulièrement avec Git.

3. Les messages de commit doivent rester explicites et suivre une convention simple, par exemple :

   ```text
   feat: ajouter une nouvelle fonctionnalité
   fix: corriger un problème
   test: ajouter ou modifier des tests
   docs: mettre à jour la documentation
   chore: effectuer une modification technique
   ci: modifier la configuration CI/CD
   ```

4. Les secrets ne doivent jamais être écrits directement dans le code ni ajoutés au dépôt Git.

   Les mots de passe, tokens et autres informations sensibles devront être transmis à l’aide de variables d’environnement, de variables CI/CD ou de fichiers locaux ignorés par Git comme `.env`.

5. Avant de poursuivre vers le TP suivant, vérifiez que les commandes, tests et points de contrôle demandés fonctionnent correctement.

## Environnement nécessaire

Pour réaliser l’ensemble des TP, prévoyez au minimum :

* Python 3.11 ou supérieur ;
* Git ;
* un éditeur de code comme VS Code ;
* un terminal ;
* Docker Desktop ou Docker Engine ;
* Docker Compose ;
* un compte GitLab.

Docker doit être installé et démarré avant les exercices utilisant les conteneurs. Vous pouvez notamment le vérifier avec :

```bash
docker version
```

La commande doit pouvoir communiquer avec le client Docker ainsi qu’avec le moteur Docker.


## Réponses aux questions

Lorsque des questions sont posées au cours d’un TP, les réponses devront être fournies dans un fichier dédié au format Markdown (`.md`) ou texte (`.txt`).

Pour chaque question :

1. recopiez la question ;
2. écrivez votre réponse juste en dessous ;
3. conservez l’ensemble des réponses dans ce fichier et ajoutez-le au projet lorsque cela est demandé.

# TP1 — Mettre l’API en boîte

## Mise en situation

Le client **StockLine** utilise une petite API d’inventaire. Aujourd’hui, elle tourne « à la main » sur le portable d’un développeur parti en congés.

Votre manager vous demande de conteneuriser cette application afin d’obtenir une image propre, légère et reproductible, qui ne s’exécute pas avec l’utilisateur `root`.

À la fin de ce TP, n’importe qui devra pouvoir lancer l’application conteneurisée à partir d’une simple commande Docker.

## Partie 1 — L’API sur votre poste

### Création du projet

Créez un nouveau projet ainsi qu’un dépôt Git associé.

Vous pouvez utiliser le nom suivant :

```text
stockline-mini
```

Organisez le projet avec deux répertoires principaux :

```text
app/
tests/
```

Le répertoire `app` contiendra le code de l’application et le répertoire `tests` contiendra les tests automatisés.

### Création de l’API

Créez le fichier :

```text
app/main.py
```

Cette première version de l’API utilise volontairement des données stockées en mémoire. Une véritable base de données sera ajoutée au TP2.

Utilisez le code suivant sans le modifier :

```python
"""StockLine mini — API d'inventaire simplifiée (version en mémoire)."""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ENVIRONNEMENT = os.environ.get("STOCKLINE_ENV", "dev")

app = FastAPI(title="StockLine mini")


class Produit(BaseModel):
    nom: str
    quantite: int
    seuil_alerte: int = 5


PRODUITS: dict[int, dict] = {
    1: {"id": 1, "nom": "Clavier mécanique", "quantite": 12, "seuil_alerte": 5},
    2: {"id": 2, "nom": "Écran 27 pouces", "quantite": 3, "seuil_alerte": 5},
    3: {"id": 3, "nom": "Câble HDMI 2 m", "quantite": 40, "seuil_alerte": 10},
}


@app.get("/sante")
def sante():
    return {"statut": "ok", "environnement": ENVIRONNEMENT}


@app.get("/produits")
def lister_produits():
    return list(PRODUITS.values())


@app.get("/produits/{produit_id}")
def lire_produit(produit_id: int):
    if produit_id not in PRODUITS:
        raise HTTPException(status_code=404, detail="produit inconnu")
    return PRODUITS[produit_id]


@app.post("/produits", status_code=201)
def creer_produit(produit: Produit):
    nouvel_id = max(PRODUITS, default=0) + 1
    PRODUITS[nouvel_id] = {"id": nouvel_id, **produit.model_dump()}
    return PRODUITS[nouvel_id]


@app.get("/alertes")
def alertes():
    """Produits dont la quantité est passée sous le seuil d'alerte."""
    return [p for p in PRODUITS.values() if p["quantite"] < p["seuil_alerte"]]
```

### Dépendances du projet

Créez deux fichiers de dépendances.

Le premier contient uniquement les dépendances nécessaires au fonctionnement de l’application.

`requirements.txt` :

```text
fastapi
uvicorn[standard]
```

Le second contient les outils nécessaires pendant le développement et les tests.

`requirements-dev.txt` :

```text
-r requirements.txt
pytest
httpx
ruff
```

La ligne :

```text
-r requirements.txt
```

permet d’installer également toutes les dépendances définies dans `requirements.txt`.

Ainsi, les dépendances nécessaires à l’exécution de l’application ne sont pas dupliquées dans le fichier destiné au développement.

### Création des tests

Créez le fichier :

```text
tests/test_api.py
```

Utilisez le code suivant sans le modifier :

```python
"""Tests de l'API StockLine mini."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sante_repond_ok():
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"


def test_liste_des_produits():
    reponse = client.get("/produits")
    assert reponse.status_code == 200
    assert len(reponse.json()) >= 3


def test_produit_inconnu_renvoie_404():
    reponse = client.get("/produits/9999")
    assert reponse.status_code == 404


def test_creation_puis_lecture_d_un_produit():
    nouveau = {"nom": "Souris sans fil", "quantite": 25, "seuil_alerte": 8}
    creation = client.post("/produits", json=nouveau)
    assert creation.status_code == 201
    produit_id = creation.json()["id"]

    relecture = client.get(f"/produits/{produit_id}")
    assert relecture.status_code == 200
    assert relecture.json()["nom"] == "Souris sans fil"


def test_alertes_detecte_le_stock_bas():
    reponse = client.get("/alertes")
    noms = [p["nom"] for p in reponse.json()]
    assert "Écran 27 pouces" in noms  # 3 en stock, seuil à 5
```

### Vérification de l’application sur le poste

Avant de conteneuriser une application, vérifiez toujours qu’elle fonctionne correctement directement sur votre poste.

Effectuez les opérations suivantes :

1. créez et activez un environnement virtuel Python ;

2. installez les dépendances de développement :

   ```bash
   pip install -r requirements-dev.txt
   ```

3. lancez les tests :

   ```bash
   python -m pytest -v
   ```

4. vérifiez le code avec Ruff :

   ```bash
   python -m ruff check app tests
   ```

5. démarrez l’API :

    ```bash
    python -m uvicorn app.main:app --port 8000
    ```

    Laissez ce terminal ouvert pendant toute la durée des vérifications : tant que cette commande est en cours d’exécution, le serveur Uvicorn reste actif et l’API est accessible.

    Pour arrêter l’API (pas maintenant), revenez dans ce terminal et utilisez le raccourci :

    ```text
    Ctrl + C
    ```

6. ouvrez votre navigateur et accédez à :

   ```text
   http://localhost:8000/sante
   ```

   Vérifiez que l’API répond correctement.

7. accédez ensuite à :

   ```text
   http://localhost:8000/alertes
   ```

   Vérifiez que la liste retournée contient uniquement le produit dont le stock est inférieur à son seuil d’alerte.

### Configuration de Git

Créez un fichier `.gitignore` permettant notamment d’exclure :

```text
.venv/
__pycache__/
*.pyc
.env
```

Ajoutez ensuite les fichiers au dépôt Git et réalisez plusieurs commits cohérents.

Utilisez des messages de commit explicites, par exemple :

```text
feat: ajouter l'API d'inventaire
test: ajouter les tests de l'API
chore: configurer les fichiers ignorés
```

### Point de contrôle

Avant de continuer vers la partie suivante, vérifiez les points suivants :

* `pytest` affiche bien :

  ```text
  5 passed
  ```

* selon les versions des bibliothèques utilisées, quelques `warnings` peuvent éventuellement apparaître pendant l’exécution des tests ; ils ne sont pas bloquants tant que les cinq tests passent correctement ;

* Ruff ne signale aucune erreur ;

* l’adresse :

  ```text
  http://localhost:8000/sante
  ```

  répond avec un statut `ok` ;

* l’adresse :

  ```text
  http://localhost:8000/alertes
  ```

  affiche uniquement le produit :

  ```json
  [
    {
      "id": 2,
      "nom": "Écran 27 pouces",
      "quantite": 3,
      "seuil_alerte": 5
    }
  ]
  ```

    * une fois toutes les vérifications terminées, revenez dans le terminal dans lequel Uvicorn est en cours d’exécution et utilisez `Ctrl + C` pour arrêter proprement le serveur avant de poursuivre.



## Partie 2 — Premier Dockerfile : ça marche, mais…

Créez un premier Dockerfile volontairement simple, nommé :

```text
Dockerfile.naif
```

Utilisez le contenu suivant :

```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Ce Dockerfile permet de construire rapidement une première image fonctionnelle de l’application.

L’objectif de cette partie est d’observer son fonctionnement, puis d’identifier les défauts de cette première approche.

### Construction de l’image

Fournissez la commande Docker permettant de construire une image à partir du fichier `Dockerfile.naif`.

L’image devra être nommée exactement :

```text
stockline-mini:naif
```

Commande :

```text



```

Exécutez ensuite votre commande et vérifiez que la construction de l’image se termine correctement.

### Lancement du conteneur

Fournissez la commande permettant de lancer un conteneur à partir de l’image :

```text
stockline-mini:naif
```

Contraintes :

* le conteneur doit être lancé en arrière-plan ;
* donnez-lui un nom explicite ;
* publiez le port `8000` du conteneur sur un port disponible de votre machine.

Commande :

```text



```

Conservez le nom du conteneur et le port choisis : ils seront utilisés dans les vérifications suivantes.

### Vérification de l’API

Dans votre navigateur, ouvrez l’adresse suivante en remplaçant `<PORT>` par le port que vous avez choisi :

```text
http://localhost:<PORT>/sante
```

Vérifiez que l’API répond correctement.

### Observation de l’image

Utilisez la commande suivante pour afficher les images correspondant au projet :

```bash
docker images stockline-mini
```

Observez la taille de l’image `stockline-mini:naif`.

Répondez à la question suivante dans votre fichier de réponses :

**Quelle est la taille approximative de l’image `stockline-mini:naif` ? Est-elle proche de 1,2 Go ?**

### Utilisateur du conteneur

Exécutez la commande suivante en remplaçant `<NOM_CONTENEUR>` par le nom utilisé lors du lancement :

```bash
docker exec <NOM_CONTENEUR> whoami
```

Observez le résultat.

Répondez à la question suivante dans votre fichier de réponses :

**Avec quel utilisateur le processus du conteneur est-il exécuté ?**


### Analyse

À partir des observations précédentes, répondez à la question suivante dans votre fichier de réponses :

**Quels sont les deux principaux problèmes que vous pouvez identifier avec cette première image Docker ?**

Appuyez-vous notamment sur :

* la taille de l’image ;
* l’utilisateur avec lequel le conteneur s’exécute.

### Nettoyage

Une fois les vérifications terminées, arrêtez et supprimez le conteneur utilisé pour cette partie.

Fournissez puis exécutez la commande permettant de réaliser ce nettoyage.

Commande :

```text



```

## Partie 3 — Le Dockerfile professionnel

La première image fonctionne, mais elle présente deux problèmes importants : elle est beaucoup trop volumineuse et le conteneur s’exécute avec l’utilisateur `root`.

Vous allez maintenant créer une version plus propre du Dockerfile.

Cette nouvelle version doit corriger quatre points :

1. utiliser une image Python plus légère avec `python:3.12-slim` ;

2. organiser les instructions afin d’installer les dépendances avant de copier le code de l’application ;

3. limiter les fichiers envoyés dans le contexte de build grâce à un fichier `.dockerignore` ;

4. exécuter l’application avec un utilisateur non-root.

### Créer le Dockerfile

Créez à la racine du projet un fichier nommé :

```text
Dockerfile
```

Utilisez le contenu suivant :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

RUN useradd --create-home apiuser
USER apiuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Créer le fichier `.dockerignore`

Créez également à la racine du projet un fichier :

```text
.dockerignore
```

Ajoutez-y :

```text
.venv/
__pycache__/
*.pyc
.git/
.env
tests/
```

Ce fichier permet d’éviter d’envoyer au contexte de build des fichiers qui ne sont pas nécessaires à l’exécution de l’application.

### Construire la nouvelle image

Construisez l’image avec le tag :

```text
stockline-mini:1.0
```

Utilisez :

```bash
docker build -t stockline-mini:1.0 .
```

Affichez ensuite les images du projet :

```bash
docker images stockline-mini
```

Comparez la taille de :

```text
stockline-mini:naif
```

avec celle de :

```text
stockline-mini:1.0
```

La nouvelle image doit être nettement plus légère.

### Vérifier le fonctionnement

Lancez un conteneur à partir de la nouvelle image :

```bash
docker run -d --name api -p 8000:8000 stockline-mini:1.0
```

Ouvrez ensuite dans votre navigateur :

```text
http://localhost:8000/sante
```

Vérifiez que l’API fonctionne toujours correctement.

### Vérifier l’utilisateur

Exécutez :

```bash
docker exec api whoami
```

Le résultat attendu est :

```text
apiuser
```

Le conteneur ne s’exécute donc plus avec l’utilisateur `root`.

### Point de contrôle

Avant de poursuivre, vérifiez que :

* l’image `stockline-mini:1.0` a bien été construite ;

* elle est nettement plus légère que `stockline-mini:naif` ;

* l’API répond correctement ;

* la commande :

  ```bash
  docker exec api whoami
  ```

  retourne :

  ```text
  apiuser
  ```

* le fichier `.dockerignore` est présent à la racine du projet.

Une fois les vérifications terminées, supprimez le conteneur :

```bash
docker rm -f api
```

### Commit

Enregistrez les nouveaux fichiers dans Git avec des commits explicites, par exemple :

```text
feat: conteneuriser l'API avec une image optimisée
chore: exclure les fichiers inutiles du contexte de build
```



## Bonus — TP1

* Ajoutez `HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/sante')"` au Dockerfile et observez la colonne `STATUS (healthy)` dans `docker ps`.
* Explorez `docker history stockline-mini:1.0` : retrouvez le poids de chaque couche et identifiez la plus lourde.

# TP2 — Brancher la vraie base

## Mise en situation

Votre image a fait bonne impression. Mais au premier redémarrage du conteneur, le client a perdu les produits qu’il avait saisis : les données étaient uniquement conservées en mémoire.

Votre manager revient avec une nouvelle demande :

> « Il faut une vraie base. Tu branches l’API sur PostgreSQL, tu me montes le tout avec Docker Compose — API, base, et un petit outil web pour regarder les données. Et je veux que les données survivent à un redémarrage, ça s’appelle un volume. »

## Partie 1 — L’API passe à PostgreSQL

### Ajout du pilote PostgreSQL

Modifiez le fichier `requirements.txt` afin d’ajouter le pilote PostgreSQL :

```text
fastapi
uvicorn[standard]
psycopg[binary]
```

### Modification de l’API

Remplacez le contenu du fichier :

```text
app/main.py
```

par la version suivante.

Prenez le temps de consulter et de comprendre le fonctionnement de ce code avant de poursuivre : plusieurs questions de compréhension seront posées juste après.

```python
"""StockLine mini — API d'inventaire adossée à PostgreSQL."""
import asyncio
import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

PRODUITS_INITIAUX = [
    ("Clavier mécanique", 12, 5),
    ("Écran 27 pouces", 3, 5),
    ("Câble HDMI 2 m", 40, 10),
]


def dsn():
    """Construit la chaîne de connexion depuis les variables d'environnement."""
    return (
        f"host={os.environ.get('DB_HOTE', 'localhost')} "
        f"port={os.environ.get('DB_PORT', '5432')} "
        f"dbname={os.environ.get('DB_NOM', 'stockline')} "
        f"user={os.environ.get('DB_UTILISATEUR', 'stockline')} "
        f"password={os.environ['DB_MOT_DE_PASSE']}"
    )


def connexion():
    return psycopg.connect(dsn(), row_factory=dict_row)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    # La base peut mettre quelques secondes à démarrer : on réessaie.
    for _ in range(10):
        try:
            with connexion() as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS produits (
                           id SERIAL PRIMARY KEY,
                           nom TEXT NOT NULL,
                           quantite INTEGER NOT NULL,
                           seuil_alerte INTEGER NOT NULL DEFAULT 5
                       )"""
                )
                nb = conn.execute(
                    "SELECT COUNT(*) AS nb FROM produits"
                ).fetchone()["nb"]
                if nb == 0:
                    conn.cursor().executemany(
                        "INSERT INTO produits (nom, quantite, seuil_alerte) "
                        "VALUES (%s, %s, %s)",
                        PRODUITS_INITIAUX,
                    )
            break
        except psycopg.OperationalError:
            await asyncio.sleep(2)
    else:
        raise RuntimeError("base de données injoignable après 10 tentatives")
    yield


app = FastAPI(title="StockLine mini", lifespan=cycle_de_vie)


class Produit(BaseModel):
    nom: str
    quantite: int
    seuil_alerte: int = 5


@app.get("/sante")
def sante():
    try:
        with connexion() as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="base de données injoignable")
    return {"statut": "ok", "base_de_donnees": "ok"}


@app.get("/produits")
def lister_produits():
    with connexion() as conn:
        return conn.execute("SELECT * FROM produits ORDER BY id").fetchall()


@app.get("/produits/{produit_id}")
def lire_produit(produit_id: int):
    with connexion() as conn:
        produit = conn.execute(
            "SELECT * FROM produits WHERE id = %s", (produit_id,)
        ).fetchone()
    if produit is None:
        raise HTTPException(status_code=404, detail="produit inconnu")
    return produit


@app.post("/produits", status_code=201)
def creer_produit(produit: Produit):
    with connexion() as conn:
        return conn.execute(
            "INSERT INTO produits (nom, quantite, seuil_alerte) "
            "VALUES (%s, %s, %s) RETURNING *",
            (produit.nom, produit.quantite, produit.seuil_alerte),
        ).fetchone()


@app.get("/alertes")
def alertes():
    """Produits dont la quantité est passée sous le seuil d'alerte."""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM produits WHERE quantite < seuil_alerte ORDER BY id"
        ).fetchall()
```

### Questions de compréhension

Avant de continuer, répondez aux questions suivantes dans votre fichier de réponses.

Pour chaque question, rappelez la question puis écrivez votre réponse juste en dessous.

1. Pourquoi le mot de passe est-il le **seul** paramètre sans valeur par défaut (`os.environ['DB_MOT_DE_PASSE']` et pas `.get(...)`) ?

2. À quoi sert la boucle de la fonction `cycle_de_vie` ? Que se passerait-il sans elle au démarrage d’une stack Docker Compose ?

3. Pourquoi écrit-on :

   ```python
   WHERE id = %s
   ```

   avec un paramètre, et jamais :

   ```python
   f"WHERE id = {produit_id}"
   ```

   Indice : injection.


## Partie 2 — Tester avec une base jetable

Pour tester cette nouvelle version de l’application, il n’est pas nécessaire d’installer PostgreSQL directement sur votre machine.

Vous allez utiliser un conteneur PostgreSQL temporaire qui servira uniquement pendant les tests.

### Lancer PostgreSQL

Lancez un conteneur PostgreSQL avec la commande suivante :

```bash
docker run -d --name db-test -p 5432:5432 \
  -e POSTGRES_DB=stockline -e POSTGRES_USER=stockline \
  -e POSTGRES_PASSWORD=devnordexia \
  postgres:16-alpine
```

Ce conteneur fournit une base PostgreSQL accessible depuis votre poste sur le port `5432`.

Il utilise les informations suivantes :

```text
Base : stockline
Utilisateur : stockline
Mot de passe : devnordexia
```

### Mettre à jour les dépendances Python

Dans la partie précédente, vous avez ajouté :

```text
psycopg[binary]
```

au fichier `requirements.txt`.

Votre environnement virtuel ayant été créé avant cette modification, réinstallez les dépendances de développement afin de récupérer également ce nouveau paquet :

```bash
pip install -r requirements-dev.txt
```

Le fichier `requirements-dev.txt` incluant lui-même `requirements.txt`, cette commande installera également `psycopg`.

### Adapter les tests

La nouvelle version de l’API utilise maintenant le mécanisme `lifespan` de FastAPI.

Lors du démarrage de l’application, ce mécanisme permet notamment :

* de tenter la connexion à PostgreSQL ;
* de créer la table `produits` si elle n’existe pas ;
* d’insérer les produits initiaux lorsque la table est vide.

Les tests doivent donc démarrer l’application de manière à exécuter correctement ce cycle de vie.

Dans le TP1, le client de test était créé directement de cette manière :

```python
client = TestClient(app)
```

Cette approche doit maintenant être remplacée par une **fixture pytest** utilisant un bloc `with`.

Modifiez le début du fichier :

```text
tests/test_api.py
```

afin d’obtenir :

```python
"""Tests de l'API StockLine mini (version PostgreSQL)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Le "with" déclenche le cycle de vie : création de la table incluse.
    with TestClient(app) as c:
        yield c
```

Cette fixture crée un client de test au moment où un test en a besoin.

Le bloc :

```python
with TestClient(app) as c:
```

permet de démarrer correctement le cycle de vie de l’application avant le test, puis de le terminer proprement à la fin.

Le mot-clé :

```python
yield
```

fournit ici le client au test qui l’utilise.

### Modifier les cinq tests

Vous devez maintenant adapter les cinq tests créés au TP1.

Le principe est simple : **supprimez l’ancien client global** :

```python
client = TestClient(app)
```

puis ajoutez le paramètre :

```python
client
```

à chaque fonction de test.

Par exemple, le test :

```python
def test_sante_repond_ok():
```

devient :

```python
def test_sante_repond_ok(client):
```

et son contenu devient :

```python
def test_sante_repond_ok(client):
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["base_de_donnees"] == "ok"
```

Effectuez la même modification pour les quatre autres tests :

```text
test_liste_des_produits
test_produit_inconnu_renvoie_404
test_creation_puis_lecture_d_un_produit
test_alertes_detecte_le_stock_bas
```

Le contenu fonctionnel de ces quatre tests reste identique à celui du TP1 : seule leur déclaration doit recevoir le paramètre `client`.

À la fin de cette étape, votre fichier doit donc toujours contenir **cinq tests**, mais ils utilisent désormais tous la fixture `client`.

### Lancer les tests

La nouvelle application exige la présence de la variable d’environnement :

```text
DB_MOT_DE_PASSE
```

Fournissez-la uniquement pour l’exécution de la commande de test :

```bash
DB_MOT_DE_PASSE=devnordexia python3 -m pytest -v
```

Sous Windows PowerShell, utilisez plutôt :

```powershell
$env:DB_MOT_DE_PASSE="devnordexia"
python -m pytest -v
```

Vérifiez ensuite le code avec Ruff :

```bash
python -m ruff check app tests
```

### Point de contrôle

Avant de continuer, vérifiez les points suivants :

* PostgreSQL est bien en cours d’exécution dans le conteneur `db-test` ;
* les cinq tests utilisent la fixture `client` ;
* `pytest` affiche :

```text
5 passed
```

* les tests utilisent maintenant une véritable base PostgreSQL au lieu des données conservées uniquement en mémoire ;
* le mot de passe de la base n’est pas écrit dans le code : il est transmis à l’application par une variable d’environnement.

Une fois les tests terminés, supprimez le conteneur PostgreSQL temporaire :

```bash
docker rm -f db-test
```

### Commit

Enregistrez les modifications avec des commits explicites, par exemple :

```text
feat: adosser l'API à PostgreSQL
test: adapter les tests au cycle de vie
```

## Partie 3 — La stack Docker Compose

Créez un fichier :

```text
compose.yaml
```

Ce fichier permettra de lancer une stack composée de trois services, d’un volume et d’un healthcheck.

Utilisez le contenu suivant :

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOTE: db
      DB_MOT_DE_PASSE: ${DB_MOT_DE_PASSE}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: stockline
      POSTGRES_USER: stockline
      POSTGRES_PASSWORD: ${DB_MOT_DE_PASSE}
    volumes:
      - donnees-db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U stockline -d stockline"]
      interval: 5s
      timeout: 3s
      retries: 10

  adminer:
    image: adminer:4
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  donnees-db:
```

### Questions de compréhension

Avant de continuer, répondez aux questions suivantes dans votre fichier de réponses.

1. Dans la configuration du service `api`, pourquoi la variable :

   ```yaml
   DB_HOTE: db
   ```

   utilise-t-elle le nom `db` au lieu d’une adresse IP ou de `localhost` ?

2. À quoi sert la configuration suivante :

   ```yaml
   depends_on:
     db:
       condition: service_healthy
   ```

   et quel est le rôle du `healthcheck` configuré sur PostgreSQL ?

3. Dans les deux services, le mot de passe est récupéré de cette manière :

   ```yaml
   ${DB_MOT_DE_PASSE}
   ```

   D’où Docker Compose récupère-t-il cette valeur et pourquoi est-il préférable de procéder ainsi plutôt que d’écrire directement le mot de passe dans `compose.yaml` ?

### Création du fichier `.env`

Créez à la racine du projet un fichier :

```text
.env
```

Ajoutez-y :

```text
DB_MOT_DE_PASSE=devnordexia
```

Ce fichier contient une information sensible et ne doit donc jamais être envoyé dans le dépôt Git.

Vérifiez que `.env` est bien présent dans votre `.gitignore`.

Vous pouvez également utiliser la commande suivante pour vérifier que Git l’ignore effectivement :

```bash
git check-ignore .env
```

Si la commande retourne :

```text
.env
```

cela signifie que le fichier est bien ignoré par Git.

### Démarrer la stack

Construisez et démarrez les services avec :

```bash
docker compose up -d --build
```

Vérifiez ensuite leur état :

```bash
docker compose ps
```

Le service PostgreSQL doit notamment apparaître comme étant en bonne santé (`healthy`).

### Vérifier l’API

Dans votre navigateur, ouvrez :

```text
http://localhost:8000/sante
```

Vérifiez que l’API répond correctement et que la base de données est accessible.

Ouvrez ensuite :

```text
http://localhost:8000/produits
```

Vérifiez que les trois produits initiaux sont présents.

### Consulter la base avec Adminer

Ouvrez Adminer dans votre navigateur :

```text
http://localhost:8080
```

Utilisez les informations suivantes pour vous connecter :

```text
Système : PostgreSQL
Serveur : db
Utilisateur : stockline
Mot de passe : devnordexia
Base de données : stockline
```

Une fois connecté, ouvrez la table :

```text
produits
```

Vérifiez que les données présentes dans PostgreSQL correspondent bien aux produits retournés par l’API.

### Point de contrôle

Avant de poursuivre, vérifiez les éléments suivants :

* les trois services sont démarrés ;

* le service `db` est indiqué comme `healthy` ;

* l’adresse :

  ```text
  http://localhost:8000/sante
  ```

  renvoie :

  ```json
  {
    "statut": "ok",
    "base_de_donnees": "ok"
  }
  ```

* l’adresse :

  ```text
  http://localhost:8000/produits
  ```

  affiche les trois produits initiaux avec les identifiants `1`, `2` et `3` ;

* Adminer permet d’accéder à la table `produits` et d’y retrouver les mêmes données ;

* le fichier `.env` est bien ignoré par Git.

### Commit

Enregistrez la configuration Docker Compose avec un commit explicite, par exemple :

```text
feat: orchestrer la stack avec docker compose
```


## Partie 4 — La preuve de la persistance

L’objectif de cette partie est de vérifier que les données enregistrées dans PostgreSQL survivent à la suppression et à la recréation des conteneurs.

### Ajouter une nouvelle donnée

Commencez par créer un nouveau produit en envoyant une requête `POST` à l’API.

Pour cette commande, utilisez **Git Bash** afin d’éviter les différences de syntaxe que l’on peut rencontrer avec certaines versions de PowerShell sous Windows.

Exécutez :

```bash
curl -X POST http://localhost:8000/produits \
  -H "Content-Type: application/json" \
  -d '{"nom":"Casque audio","quantite":7,"seuil_alerte":3}'
```

Vérifiez que l’API retourne le produit créé avec un nouvel identifiant.

Le produit doit notamment avoir pour identifiant :

```text
4
```

### Arrêter et supprimer les conteneurs

Arrêtez ensuite la stack Docker Compose :

```bash
docker compose down
```

Cette commande arrête et supprime les conteneurs ainsi que le réseau créé par Docker Compose, mais **ne supprime pas le volume contenant les données PostgreSQL**.

Vérifiez que les conteneurs ne sont plus en cours d’exécution :

```bash
docker compose ps
```

### Relancer la stack

Redémarrez ensuite les services :

```bash
docker compose up -d
```

Attendez que les services soient correctement démarrés.

Vous pouvez vérifier leur état avec :

```bash
docker compose ps
```

### Vérifier la persistance

Dans votre navigateur, ouvrez :

```text
http://localhost:8000/produits/4
```

Vérifiez que le produit créé avant l’arrêt des conteneurs est toujours présent.

Le résultat attendu correspond au produit :

```json
{
  "id": 4,
  "nom": "Casque audio",
  "quantite": 7,
  "seuil_alerte": 3
}
```

Cela montre que les conteneurs ont été supprimés puis recréés, mais que les données ont été conservées grâce au volume Docker.

### Tester la suppression du volume

Effectuez maintenant une seconde expérience.

Arrêtez cette fois la stack en supprimant également les volumes :

```bash
docker compose down -v
```

Le paramètre :

```text
-v
```

demande à Docker Compose de supprimer également les volumes associés à la stack.

Redémarrez ensuite les services :

```bash
docker compose up -d
```

Une fois les services disponibles, ouvrez de nouveau :

```text
http://localhost:8000/produits/4
```

Le produit précédemment créé ne doit plus exister.

### Point de contrôle

À la fin de cette partie, vous devez avoir vérifié les deux comportements suivants :

1. après :

   ```bash
   docker compose down
   docker compose up -d
   ```

   le produit ajouté précédemment est toujours présent ;

2. après :

   ```bash
   docker compose down -v
   docker compose up -d
   ```

   le produit ajouté précédemment a disparu, car le volume PostgreSQL a été supprimé.

Vous devez donc être capable d’expliquer la différence entre :

```bash
docker compose down
```

et :

```bash
docker compose down -v
```

ainsi que le rôle joué par le volume dans la persistance des données.

### Quelques commandes d’exploitation

Avant de terminer le TP, testez également les commandes suivantes.

Suivre les logs de l’API :

```bash
docker compose logs -f api
```

Utilisez `Ctrl + C` pour quitter l’affichage continu des logs.

Exécuter directement une requête SQL dans le conteneur PostgreSQL :

```bash
docker compose exec db psql -U stockline \
  -c "SELECT nom, quantite FROM produits;"
```

Lorsque toutes les vérifications sont terminées, arrêtez complètement la stack et supprimez ses volumes :

```bash
docker compose down -v
```

## Bonus

* Ajoutez un service `front` : image `nginx:alpine` qui sert une page `index.html` statique (montée en volume) affichant « StockLine mini » et un lien vers `/produits`.
* Dans Adminer, ajoutez un produit à la main, puis vérifiez qu’il apparaît dans `curl http://localhost:8000/produits` : l’API et Adminer regardent la même base.


# TP3 — Bienvenue sur GitLab

## Mise en situation

Nordexia héberge ses projets sur **GitLab**. Vous connaissez GitHub du cursus : tant mieux, 90 % des concepts se transposent — une *pull request* s’appelle ici une **merge request** (MR), et GitLab intègre en plus la CI/CD et un registre d’images que vous utiliserez aux TP suivants.

> « Monte le projet stockline-mini sur notre GitLab, ouvre les tickets de ce qui reste à faire, et fais passer ta première modification par une merge request. Personne ne pousse sur main directement ici. »


## Partie 1 — Le projet GitLab

### Créer le projet

Sur GitLab, créez un nouveau projet :

**New project → Create blank project**

Utilisez les paramètres suivants :

```text
Nom du projet : stockline-mini
Visibilité : Public
```

Ne demandez pas à GitLab d’initialiser automatiquement le dépôt avec un fichier README.

Votre projet existe déjà sur votre poste avec son historique Git issu des TP précédents. Le dépôt distant doit donc être créé vide afin de pouvoir y envoyer directement votre projet existant.

### Envoyer le projet sur GitLab

Reliez votre dépôt Git local au projet GitLab que vous venez de créer.

Ajoutez GitLab comme dépôt distant en utilisant l’adresse proposée sur la page de votre projet.

Par exemple :

```bash
git remote add origin https://gitlab.com/<votre-compte>/stockline-mini.git
```

Envoyez ensuite la branche `main` vers GitLab :

```bash
git push -u origin main
```

Utilisez la méthode d’authentification GitLab déjà configurée sur votre poste.

### Point de contrôle

Ouvrez votre projet `stockline-mini` sur GitLab et vérifiez que :

* les fichiers réalisés lors des TP1 et TP2 sont présents ;
* l’historique des commits a bien été conservé ;
* la branche `main` ou `master` est présente ;
* le fichier `.env` **n’apparaît pas** dans le dépôt.

Si le fichier `.env` apparaît sur GitLab, ne poursuivez pas avant d’avoir corrigé le problème.


## Partie 2 — Les tickets

Dans un projet GitLab, les tâches à réaliser peuvent être suivies à l’aide des **issues**.

Vous allez créer deux issues correspondant à deux améliorations du projet.

Pour créer une issue dans GitLab :

* interface française : **Plan → Éléments de travail → Nouvel élément** ;
* interface anglaise : **Plan → Work items → New item**.

Choisissez ensuite le type **Issue**, puis renseignez son titre et sa description.


### Issue 1 — Exposer la version de l’application

Créez une première issue avec le titre :

```text
Exposer la version de l'application sur /sante
```

Dans la description, expliquez en quelques phrases que l’endpoint :

```text
/sante
```

indique actuellement si l’application et la base de données fonctionnent correctement, mais qu’il ne permet pas de savoir précisément quelle version de l’application est en cours d’exécution.

L’objectif de cette évolution sera donc d’ajouter cette information à la réponse de `/sante`.

Par exemple, à terme, une réponse pourra contenir une information de ce type :

```json
{
  "statut": "ok",
  "base_de_donnees": "ok",
  "version": "dev"
}
```

Cette issue sera traitée dans la partie suivante du TP.

### Issue 2 — Compléter le README

Créez une deuxième issue avec le titre :

```text
Compléter le README : lancement via Docker Compose
```

L’objectif de cette issue est de documenter correctement la manière de lancer le projet.

Dans la description de l’issue, ajoutez une liste à cocher indiquant les éléments qui devront être ajoutés au README.

Par exemple :

```markdown
- [ ] Indiquer les prérequis
- [ ] Expliquer la création du fichier .env
- [ ] Donner la commande de démarrage avec Docker Compose
- [ ] Indiquer les URL permettant d’accéder à l’API et à Adminer
- [ ] Donner la commande permettant d’arrêter la stack
```

Cette issue ne sera pas nécessairement traitée immédiatement : elle sert également à représenter une tâche restant à faire dans le projet.

### Ajouter des labels

Créez et attribuez les labels suivants :

```text
amelioration
documentation
```

Associez :

* le label `amelioration` à l’issue concernant `/sante` ;
* le label `documentation` à l’issue concernant le README.

Créez également un label :

```text
en-cours
```

### Utiliser l’Issue Board

Ouvrez :

```text
Plan → Issue boards
```

Créez une liste basée sur le label :

```text
en-cours
```

Déplacez ensuite l’issue :

```text
Exposer la version de l'application sur /sante
```

dans cette liste.

Vous disposez maintenant d’un mini tableau Kanban permettant de visualiser les tâches du projet et leur état d’avancement.



## Partie 3 — La première merge request

Vous allez maintenant traiter l’issue n° 1 en suivant un workflow GitLab complet.

### Créer la branche et la merge request depuis l’issue

Ouvrez l’issue :

```text
Exposer la version de l'application sur /sante
```

Depuis la page de l’issue, utilisez le bouton :

```text
Create merge request
```

GitLab crée alors automatiquement :

* une branche dédiée à cette issue ;
* une merge request associée ;
* un lien entre l’issue, la branche et la merge request.

Le nom de la branche sera généralement proche de :

```text
1-exposer-la-version-de-l-application-sur-sante
```

### Récupérer la branche en local

Dans votre terminal, récupérez les nouvelles références du dépôt distant :

```bash
git fetch origin
```

Puis placez-vous sur la branche créée par GitLab :

```bash
git switch 1-exposer-la-version-de-l-application-sur-sante
```

Adaptez le nom si GitLab a généré une branche légèrement différente.

### Modifier l’application

Vous devez maintenant faire évoluer l’endpoint :

```text
/sante
```

afin qu’il indique également la version de l’application.

Ouvrez :

```text
app/main.py
```

Ajoutez une constante permettant de récupérer la version depuis une variable d’environnement.

Placez cette ligne avec les autres constantes ou éléments de configuration, après les imports :

```python
VERSION = os.environ.get("VERSION_APP", "dev")
```

Cette ligne signifie :

* si la variable d’environnement `VERSION_APP` existe, sa valeur sera utilisée ;
* sinon, la version utilisée par défaut sera `dev`.

Repérez ensuite la fonction :

```python
@app.get("/sante")
def sante():
```

Actuellement, sa réponse contient :

```python
return {"statut": "ok", "base_de_donnees": "ok"}
```

Modifiez cette réponse afin d’y ajouter la version :

```python
return {
    "statut": "ok",
    "base_de_donnees": "ok",
    "version": VERSION,
}
```

L’endpoint `/sante` doit donc maintenant pouvoir retourner une réponse du type :

```json
{
  "statut": "ok",
  "base_de_donnees": "ok",
  "version": "dev"
}
```

### Adapter le test

Ouvrez ensuite :

```text
tests/test_api.py
```

Repérez le test :

```python
test_sante_repond_ok
```

Ce test doit maintenant vérifier également que la réponse contient bien la clé :

```text
version
```

Ajoutez donc l’assertion suivante :

```python
assert "version" in reponse.json()
```

Le test doit conserver les vérifications déjà présentes et ajouter cette nouvelle vérification.

### Vérifier les modifications localement

Avant de lancer les tests, rappelez-vous que l’application utilise maintenant PostgreSQL.

Les tests ont donc besoin :

* d’une base PostgreSQL accessible ;
* de la variable d’environnement `DB_MOT_DE_PASSE`.

Si aucun conteneur PostgreSQL de test n’est actuellement lancé, démarrez-en un avec :

```bash
docker run -d --name db-test -p 5432:5432 -e POSTGRES_DB=stockline -e POSTGRES_USER=stockline -e POSTGRES_PASSWORD=devnordexia postgres:16-alpine
```

Définissez ensuite la variable d’environnement nécessaire.

Sous PowerShell :

```powershell
$env:DB_MOT_DE_PASSE="devnordexia"
```

Puis lancez les tests :

```bash
python -m pytest -v
```

Vérifiez que les cinq tests passent correctement.

Vérifiez également le code avec Ruff :

```bash
python -m ruff check app tests
```

Une fois les vérifications terminées, supprimez le conteneur PostgreSQL temporaire :

```bash
docker rm -f db-test
```


### Commit et push de la branche

Enregistrez vos modifications avec un commit explicite, par exemple :

```bash
git add .
git commit -m "feat: exposer la version de l'application sur /sante"
```

Envoyez ensuite votre branche vers GitLab :

```bash
git push -u origin 1-exposer-la-version-de-l-application-sur-sante
```

Adaptez une nouvelle fois le nom de la branche si nécessaire.

### Vérifier la merge request

Retournez sur GitLab et ouvrez la merge request associée.

Vérifiez que sa description contient :

```text
Closes #1
```

Cette instruction permet à GitLab de fermer automatiquement l’issue n° 1 lorsque la merge request sera fusionnée.

### Effectuer une revue du code

Dans la merge request, ouvrez l’onglet :

```text
Changes
```

Relisez les modifications réalisées.

Ajoutez un commentaire sur une ligne du code modifié, puis :

1. répondez au commentaire ;
2. marquez ensuite le fil de discussion comme résolu.

L’objectif est de manipuler le mécanisme de revue de code intégré à GitLab.

### Fusionner la merge request

Lorsque les modifications ont été vérifiées, fusionnez la merge request.

Activez l’option :

```text
Delete source branch
```

afin que la branche de travail soit supprimée sur GitLab après le merge.

Une fois la fusion terminée, revenez dans votre terminal et replacez-vous sur `main` :

```bash
git switch main
```

Récupérez ensuite les modifications fusionnées :

```bash
git pull
```

Votre branche locale `main` contient maintenant la modification réalisée dans la merge request.

### Vérifier l’application après le merge

Comme le code de l’application a changé, l’image Docker utilisée par la stack doit être reconstruite.

Relancez donc Docker Compose avec :

```bash
docker compose up -d --build
```

L’option :

```text
--build
```

force Docker Compose à reconstruire l’image de l’API afin d’y intégrer la nouvelle version du code.

Une fois les services démarrés, ouvrez dans votre navigateur :

```text
http://localhost:8000/sante
```

La réponse doit maintenant contenir :

```json
{
  "statut": "ok",
  "base_de_donnees": "ok",
  "version": "dev"
}
```

### Point de contrôle

Avant de poursuivre, vérifiez que :

* la merge request a bien été fusionnée ;
* l’issue n° 1 est passée automatiquement à l’état `Closed` ;
* la branche de travail a été supprimée sur GitLab ;
* votre branche locale `main` contient les modifications ;
* les tests passent toujours ;
* l’endpoint `/sante` retourne maintenant la clé `version`.

### Protéger la branche `main`

Jusqu’à présent, il était encore possible de pousser directement des modifications sur `main`.

Vous allez maintenant protéger cette branche afin d’imposer l’utilisation des merge requests.

Dans GitLab, ouvrez les paramètres du projet puis rendez-vous dans :

```text
Settings → Repository → Branch rules
```

Sélectionnez la branche :

```text
main
```

Configurez la règle afin qu’aucun utilisateur ne puisse pousser directement sur cette branche.

Le principe recherché est le suivant :

* les modifications doivent être réalisées sur une branche de travail ;
* elles doivent passer par une merge request ;
* `main` ne doit plus recevoir de push direct.

Une fois la règle appliquée, testez-la depuis votre terminal.

Placez-vous sur `main`, puis tentez :

```bash
git push origin main
```

Le push direct doit être refusé par GitLab.

Vous devriez obtenir un message indiquant que vous n’êtes pas autorisé à pousser directement sur une branche protégée.

À partir de maintenant, les modifications destinées à `main` devront passer par une merge request.

## Bonus

* Traitez l’issue n° 2 (README) par le même flux complet, en ajoutant une **milestone** « Révisions » regroupant les deux issues.
* Explorez *Plan → Issue boards* en mode multi-listes (À faire / En cours / Terminé) : c’est l’outil de pilotage quotidien de beaucoup d’équipes.


# TP4 — Le pipeline qui dit non

## Mise en situation

> « Ta MR d’hier était bien, mais c’est moi qui ai dû lancer les tests à la main pour vérifier. Ce n’est pas ton travail de me le prouver, c’est le travail de la machine : mets-moi un pipeline. Lint et tests sur chaque push, et une MR dont le pipeline est rouge ne doit pas pouvoir être fusionnée. »

## Partie 1 — Le premier pipeline

Vous allez commencer par mettre en place un pipeline GitLab CI très simple afin de comprendre son fonctionnement avant d’ajouter les véritables étapes de vérification.

### Créer une branche dédiée

Créez une nouvelle branche pour travailler sur la configuration CI :

```bash id="boe8j0"
git switch -c ci/pipeline
```

Toutes les modifications de cette partie seront réalisées sur cette branche.

### Créer le fichier de pipeline

À la racine du projet, créez le fichier :

```text id="czxmy9"
.gitlab-ci.yml
```

Utilisez le contenu suivant :

```yaml id="5m8qra"
stages:
  - verification

dire-bonjour:
  stage: verification
  image: python:3.12-slim
  script:
    - python --version
    - echo "Pipeline exécuté par $GITLAB_USER_LOGIN sur $CI_COMMIT_BRANCH"
```

Ce premier pipeline contient :

* un stage nommé `verification` ;
* un job nommé `dire-bonjour` ;
* une image Docker `python:3.12-slim` dans laquelle le job sera exécuté ;
* deux commandes simples permettant de vérifier que le job s’exécute correctement.

### Envoyer la configuration sur GitLab

Ajoutez et committez le fichier :

```bash id="64j50g"
git add .gitlab-ci.yml
git commit -m "ci: ajouter le premier pipeline"
```

Envoyez ensuite votre branche sur GitLab :

```bash id="h89uk8"
git push -u origin ci/pipeline
```

Le push doit automatiquement déclencher un pipeline GitLab.

### Vérifier l’exécution du pipeline

Sur GitLab, ouvrez votre projet puis rendez-vous dans :

```text id="byjz7s"
Build → Pipelines
```

Vous devez voir apparaître un nouveau pipeline associé à la branche :

```text id="avvhhw"
ci/pipeline
```

Ouvrez ce pipeline, puis cliquez sur le job :

```text id="sjw8jc"
dire-bonjour
```

Consultez la console du job et vérifiez les éléments suivants.

La commande :

```bash id="wvz7n7"
python --version
```

doit afficher une version de Python 3.12.

Vous devez également retrouver le résultat de la commande :

```bash id="rx4skt"
echo "Pipeline exécuté par $GITLAB_USER_LOGIN sur $CI_COMMIT_BRANCH"
```

avec les variables remplacées automatiquement par GitLab.

Vous devriez donc obtenir une ligne ressemblant à :

```text id="xb3hdt"
Pipeline exécuté par <votre-login> sur ci/pipeline
```

Le login affiché doit correspondre à votre compte GitLab et le nom de branche doit correspondre à la branche ayant déclenché le pipeline.

### Ce qu’il faut observer

Lorsque le pipeline est exécuté, GitLab :

1. récupère votre dépôt ;

2. lance un environnement de travail basé sur l’image :

   ```text
   python:3.12-slim
   ```

3. exécute les commandes du bloc `script` ;

4. affiche leur sortie dans la console du job.

Les variables :

```text id="ra3djs"
$GITLAB_USER_LOGIN
$CI_COMMIT_BRANCH
```

sont fournies automatiquement par GitLab CI/CD.

### Point de contrôle

Avant de poursuivre, vérifiez que :

* le pipeline s’est déclenché automatiquement après le push ;
* le pipeline est vert ;
* le job `dire-bonjour` est terminé avec succès ;
* la console affiche bien une version de Python 3.12 ;
* votre login GitLab apparaît dans le message affiché par `echo` ;
* la branche affichée est bien `ci/pipeline`.

Une fois ces éléments vérifiés, vous avez validé le fonctionnement de votre premier pipeline GitLab CI.


## Partie 2 — Lint + tests, comme en vrai

Remplacez le contenu actuel du fichier `.gitlab-ci.yml` par la configuration suivante.

Vos tests ont maintenant besoin de PostgreSQL. GitLab peut lancer des conteneurs supplémentaires à côté du conteneur principal du job grâce au mécanisme des `services`.

```yaml
stages:
  - qualite

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

default:
  image: python:3.12-slim
  cache:
    key:
      files:
        - requirements-dev.txt
    paths:
      - .cache/pip

lint:
  stage: qualite
  script:
    - pip install ruff
    - ruff check app tests

tests:
  stage: qualite
  services:
    - name: postgres:16-alpine
      alias: db
  variables:
    POSTGRES_DB: stockline
    POSTGRES_USER: stockline
    POSTGRES_PASSWORD: motdepasse-ci
    DB_HOTE: db
    DB_MOT_DE_PASSE: motdepasse-ci
  script:
    - pip install -r requirements-dev.txt
    - python -m pytest -v --junitxml=rapport-tests.xml
  artifacts:
    when: always
    reports:
      junit: rapport-tests.xml
```

### Questions de compréhension

Répondez aux questions suivantes dans votre fichier de réponses.

1. Les jobs `lint` et `tests` utilisent tous les deux :

   ```yaml
   stage: qualite
   ```

   Que se passe-t-il lorsque plusieurs jobs appartiennent au même stage ? Sont-ils exécutés l’un après l’autre ou en parallèle ?

2. Dans le job `tests`, on trouve :

   ```yaml
   services:
     - name: postgres:16-alpine
       alias: db
   ```

   À quoi sert ce service PostgreSQL ?

   Pourquoi lui attribue-t-on l’alias :

   ```text
   db
   ```

   et pourquoi la variable :

   ```yaml
   DB_HOTE: db
   ```

   permet-elle à l’application testée de se connecter à cette base ?

   Expliquez également la différence de rôle entre :

   ```text
   POSTGRES_*
   ```

   et :

   ```text
   DB_*
   ```

   dans cette configuration.

   Enfin, pourquoi le mot de passe :

   ```text
   motdepasse-ci
   ```

   n’est-il pas considéré ici comme un véritable secret ?

3. La configuration suivante est présente dans la section `default` :

   ```yaml
   cache:
     key:
       files:
         - requirements-dev.txt
     paths:
       - .cache/pip
   ```

   À quoi sert ce cache ?

   Que se passe-t-il tant que le fichier :

   ```text
   requirements-dev.txt
   ```

   ne change pas ?

4. Le job `tests` contient également :

   ```yaml
   artifacts:
     when: always
     reports:
       junit: rapport-tests.xml
   ```

   À quoi sert le fichier :

   ```text
   rapport-tests.xml
   ```

   généré par pytest ?

   Pourquoi est-il déclaré comme rapport `junit` dans GitLab ?

   Quel intérêt présente :

   ```yaml
   when: always
   ```

   lorsque les tests échouent ?

### Envoyer la nouvelle pipeline

Enregistrez les modifications dans Git :

```bash
git add .gitlab-ci.yml
git commit -m "ci: ajouter le lint et les tests au pipeline"
```

Envoyez ensuite la branche :

```bash
git push
```

Le nouveau pipeline doit démarrer automatiquement sur GitLab.

### Vérifier le pipeline

Dans GitLab, ouvrez :

```text
Build → Pipelines
```

Puis ouvrez le nouveau pipeline.

Vous devez maintenant voir deux jobs dans le stage :

```text
qualite
```

Les jobs sont :

```text
lint
tests
```

Comme ils appartiennent au même stage, ils doivent pouvoir s’exécuter en parallèle.

Ouvrez le job `tests` et vérifiez dans sa console que pytest affiche :

```text
5 passed
```

Le rapport JUnit généré par pytest doit également être récupéré par GitLab.

Relancez ensuite le pipeline une seconde fois avec l’option :

```text
Run again
```

Observez la phase d’installation des dépendances et comparez-la avec le premier lancement.

Le cache pip doit permettre d’accélérer les installations lorsque `requirements-dev.txt` n’a pas changé.

### Merge request

Lorsque le pipeline est entièrement vert, ouvrez une merge request de :

```text
ci/pipeline
```

vers :

```text
main
```

Vérifiez une dernière fois que les deux jobs sont réussis avant de fusionner la merge request.

### Point de contrôle

Avant de poursuivre, vérifiez que :

* le pipeline contient bien un stage `qualite` ;

* les jobs `lint` et `tests` apparaissent dans ce même stage ;

* les deux jobs passent au vert ;

* le job `tests` affiche bien :

  ```text
  5 passed
  ```

* PostgreSQL a bien été utilisé comme service pendant les tests ;

* le rapport JUnit a été généré ;

* une seconde exécution du pipeline montre l’utilisation du cache pip ;

* la merge request vers `main` a été fusionnée uniquement après validation du pipeline.



## Partie 3 — Le pipeline garde la porte

Un pipeline n’est réellement utile que s’il peut empêcher qu’un code défectueux soit fusionné dans `main`.

Vous allez maintenant configurer GitLab pour bloquer une merge request lorsque son pipeline échoue, puis provoquer volontairement un échec pour vérifier que cette protection fonctionne.

### Bloquer les merge requests lorsque le pipeline échoue

Dans GitLab, ouvrez :

```text
Settings → Merge requests
```

Activez l’option :

```text
Pipelines must succeed
```

Si l’option suivante est proposée, activez-la également :

```text
Enable merged results pipelines
```

Enregistrez la configuration.

À partir de maintenant, une merge request dont le pipeline est en échec ne doit plus pouvoir être fusionnée.

### Introduire volontairement un bug

Créez une nouvelle branche :

```bash
git switch -c feature/agrandir-le-seuil
```

Ouvrez le fichier :

```text
app/main.py
```

Repérez la fonction :

```python
@app.get("/alertes")
def alertes():
```

Dans la requête SQL utilisée par cette fonction, vous devez actuellement avoir :

```python
"SELECT * FROM produits WHERE quantite < seuil_alerte ORDER BY id"
```

Modifiez volontairement la comparaison afin d’obtenir :

```python
"SELECT * FROM produits WHERE quantite > seuil_alerte ORDER BY id"
```

Vous venez d’introduire un bug métier.

L’application va désormais considérer comme produits en alerte ceux dont la quantité est **supérieure** au seuil, alors que le comportement attendu est l’inverse.

### Committer et envoyer le bug

Enregistrez cette modification :

```bash
git add app/main.py
git commit -m "feat: élargir la détection d'alertes"
```

Envoyez ensuite la branche sur GitLab :

```bash
git push -u origin feature/agrandir-le-seuil
```

Créez une merge request vers :

```text
main
```

### Observer l’échec du pipeline

Le pipeline associé à cette merge request doit échouer.

Ouvrez le pipeline puis le job :

```text
tests
```

Le test suivant doit être en échec :

```text
test_alertes_detecte_le_stock_bas
```

Le test vérifie notamment que l’élément :

```text
Écran 27 pouces
```

est bien considéré comme un produit en alerte lorsque sa quantité est inférieure à son seuil.

Avec la comparaison volontairement inversée, ce comportement n’est plus respecté.

Vérifiez également dans la merge request que le bouton permettant de fusionner est bloqué tant que le pipeline est rouge.

Consultez, si disponible, la section présentant les résultats des tests afin de retrouver le test en échec remonté grâce au rapport JUnit.

### Corriger le bug

Revenez dans :

```text
app/main.py
```

et rétablissez la condition correcte :

```python
"SELECT * FROM produits WHERE quantite < seuil_alerte ORDER BY id"
```

Enregistrez la correction :

```bash
git add app/main.py
git commit -m "fix: rétablir la condition d'alerte"
```

Envoyez la correction sur la même branche :

```bash
git push
```

Un nouveau pipeline doit démarrer automatiquement.

### Vérifier le retour au vert

Cette fois, vérifiez que :

* le job `lint` passe ;
* le job `tests` passe ;
* pytest affiche bien les cinq tests réussis ;
* le pipeline complet est vert ;
* la merge request peut de nouveau être fusionnée.

Fusionnez ensuite la merge request.

### Point de contrôle

À la fin de cette partie, vous devez avoir observé les trois étapes suivantes :

1. une modification contenant un bug provoque un pipeline rouge ;

2. la merge request ne peut pas être fusionnée tant que le pipeline échoue ;

3. après correction et nouveau push, le pipeline repasse au vert et la fusion redevient possible.

Le bug volontaire ne doit donc jamais avoir atteint la branche `main`.

## Bonus

* Ajoutez un job `formatage` (stage `qualite`) avec `ruff format --check app tests`, et constatez qu’un fichier mal formaté casse le pipeline.
* Ajoutez le **badge pipeline** dans le README :
  *Settings → CI/CD → General pipelines → Pipeline status* fournit le Markdown.
* Regardez *Settings → CI/CD → Runners* : identifiez les runners partagés qui ont exécuté vos jobs (`saas-linux-small-amd64`, le plus souvent).
