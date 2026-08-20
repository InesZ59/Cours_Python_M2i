"""StockLine Lite — API d'inventaire, version allégée du bloc CL-LINUX.
 
Version SQLite de l'application fil rouge StockLine (la version complète
FastAPI + PostgreSQL arrive avec les blocs CL-AWS1 / CL-TP1). La base est
gérée avec le module sqlite3 de la bibliothèque standard : aucun serveur
de base de données à installer.
 
Le chemin du fichier SQLite est lu dans la variable d'environnement
STOCKLINE_DB (défaut : ./stockline.db ; en production, l'unité systemd
fournit /opt/stockline/data/stockline.db).
 
Lancement en développement :
    uvicorn main:app --reload
 
Lancement en production (voir stockline.service) :
    /opt/stockline/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
"""
 
import os
import sqlite3
from contextlib import asynccontextmanager
 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
 
# Chemin de la base SQLite, configurable sans toucher au code :
# c'est l'unité systemd (Environment=STOCKLINE_DB=...) qui décide en production.
CHEMIN_BASE = os.environ.get("STOCKLINE_DB", "./stockline.db")
 
 
def ouvrir_connexion() -> sqlite3.Connection:
    """Ouvre une connexion SQLite (clés étrangères activées, colonnes par nom)."""
    connexion = sqlite3.connect(CHEMIN_BASE)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion
 
 
def creer_tables() -> None:
    """Crée les tables produits et mouvements si elles n'existent pas."""
    with ouvrir_connexion() as connexion:
        connexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS produits (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nom  TEXT NOT NULL,
                sku  TEXT NOT NULL UNIQUE,
                prix REAL NOT NULL
            );
 
            CREATE TABLE IF NOT EXISTS mouvements (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                produit_id INTEGER NOT NULL REFERENCES produits (id),
                quantite   INTEGER NOT NULL,
                horodatage TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
 
 
@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    """Initialise la base au démarrage de l'application."""
    creer_tables()
    yield
 
 
app = FastAPI(
    title="StockLine Lite",
    description="API d'inventaire — version SQLite du bloc CL-LINUX (Utopios).",
    version="0.3.0",
    lifespan=cycle_de_vie,
)
 
 
class ProduitEntree(BaseModel):
    """Corps attendu pour la création d'un produit."""
 
    nom: str = Field(min_length=1, description="Nom commercial du produit")
    sku: str = Field(min_length=1, description="Référence unique (Stock Keeping Unit)")
    prix: float = Field(ge=0, description="Prix unitaire en euros")
 
 
class MouvementEntree(BaseModel):
    """Corps attendu pour un mouvement de stock (quantité signée)."""
 
    produit_id: int = Field(description="Identifiant du produit concerné")
    quantite: int = Field(description="Positive = entrée en stock, négative = sortie")
 
 
def produit_existe(connexion: sqlite3.Connection, produit_id: int) -> bool:
    """Indique si un produit avec cet identifiant est présent en base."""
    ligne = connexion.execute(
        "SELECT 1 FROM produits WHERE id = ?", (produit_id,)
    ).fetchone()
    return ligne is not None
 
 
@app.get("/produits")
def lister_produits() -> list[dict]:
    """Liste tous les produits du catalogue."""
    with ouvrir_connexion() as connexion:
        lignes = connexion.execute(
            "SELECT id, nom, sku, prix FROM produits ORDER BY id"
        ).fetchall()
    return [dict(ligne) for ligne in lignes]
 
 
@app.post("/produits", status_code=201)
def creer_produit(produit: ProduitEntree) -> dict:
    """Crée un produit ; refuse (409) les SKU déjà présents en base."""
    with ouvrir_connexion() as connexion:
        try:
            curseur = connexion.execute(
                "INSERT INTO produits (nom, sku, prix) VALUES (?, ?, ?)",
                (produit.nom, produit.sku, produit.prix),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409, detail=f"Le SKU '{produit.sku}' existe déjà"
            )
        return {"id": curseur.lastrowid, **produit.model_dump()}
 
 
@app.get("/mouvements")
def lister_mouvements() -> list[dict]:
    """Liste tous les mouvements de stock, du plus récent au plus ancien."""
    with ouvrir_connexion() as connexion:
        lignes = connexion.execute(
            "SELECT id, produit_id, quantite, horodatage"
            " FROM mouvements ORDER BY id DESC"
        ).fetchall()
    return [dict(ligne) for ligne in lignes]
 
 
@app.post("/mouvements", status_code=201)
def creer_mouvement(mouvement: MouvementEntree) -> dict:
    """Enregistre un mouvement ; refuse (404) les produits inconnus."""
    with ouvrir_connexion() as connexion:
        if not produit_existe(connexion, mouvement.produit_id):
            raise HTTPException(
                status_code=404,
                detail=f"Produit {mouvement.produit_id} inconnu",
            )
        curseur = connexion.execute(
            "INSERT INTO mouvements (produit_id, quantite) VALUES (?, ?)",
            (mouvement.produit_id, mouvement.quantite),
        )
        return {"id": curseur.lastrowid, **mouvement.model_dump()}
 
 
@app.get("/stocks/{produit_id}")
def lire_stock(produit_id: int) -> dict:
    """Calcule le stock courant d'un produit (somme signée des mouvements)."""
    with ouvrir_connexion() as connexion:
        if not produit_existe(connexion, produit_id):
            raise HTTPException(
                status_code=404, detail=f"Produit {produit_id} inconnu"
            )
        ligne = connexion.execute(
            "SELECT COALESCE(SUM(quantite), 0) AS stock"
            " FROM mouvements WHERE produit_id = ?",
            (produit_id,),
        ).fetchone()
    return {"produit_id": produit_id, "stock": ligne["stock"]}
 
 
@app.get("/sante")
def verifier_sante() -> dict:
    """Health check : l'API répond et la base est réellement accessible."""
    try:
        with ouvrir_connexion() as connexion:
            connexion.execute("SELECT 1")
    except sqlite3.Error as erreur:
        raise HTTPException(
            status_code=503, detail=f"Base inaccessible : {erreur}"
        )
    return {"statut": "ok", "base": "accessible"}