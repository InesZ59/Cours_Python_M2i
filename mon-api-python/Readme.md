# API Python Flask à déployer sur Amazon EC2

Ce dépôt contient une petite API Python Flask conçue pour un TP AWS EC2.

## Objectif

Déployer cette application sur une instance Amazon EC2, la rendre accessible sur le port `5000`, puis la configurer comme service `systemd` afin qu'elle démarre automatiquement au redémarrage de l'instance.

## Pré-requis

- Une instance EC2 Amazon Linux 2023
- Une adresse IPv4 publique
- Un accès SSH fonctionnel
- Le port 22 autorisé depuis votre poste dans le Security Group

## 1. Installer Git

```bash
sudo dnf install git -y
```

## 2. Cloner le dépôt

Depuis le répertoire personnel de `ec2-user` :

```bash
cd /home/ec2-user
```

Puis clonez votre dépôt :

```bash
git clone URL_DU_DEPOT
```

Le dossier obtenu doit s'appeler :

```text
/home/ec2-user/mon-api-python
```

Si votre dépôt porte un autre nom, adaptez les chemins dans `mon-api.service`.

## 3. Entrer dans le projet

```bash
cd /home/ec2-user/mon-api-python
```

## 4. Créer l'environnement virtuel Python

```bash
python3 -m venv venv
```

Activez-le :

```bash
source venv/bin/activate
```

## 5. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 6. Tester l'application manuellement

```bash
python app.py
```

L'application écoute sur :

```text
0.0.0.0:5000
```

Depuis un second terminal SSH, vous pouvez tester localement :

```bash
curl http://localhost:5000
```

Puis arrêtez l'application avec :

```text
Ctrl+C
```

## 7. Ouvrir le port 5000 dans le Security Group

Dans la console AWS, ajoutez une règle entrante :

```text
Type        Custom TCP
Port        5000
Source      0.0.0.0/0
```

Cette exposition publique est volontaire dans le cadre du TP.

## 8. Installer le service systemd

Depuis le dossier du projet :

```bash
sudo cp mon-api.service /etc/systemd/system/mon-api.service
```

Rechargez systemd :

```bash
sudo systemctl daemon-reload
```

Activez le démarrage automatique :

```bash
sudo systemctl enable mon-api
```

Démarrez le service :

```bash
sudo systemctl start mon-api
```

Vérifiez son état :

```bash
sudo systemctl status mon-api
```

Vous devez obtenir un état proche de :

```text
Active: active (running)
```

## 9. Tester depuis votre poste

Dans un navigateur :

```text
http://ADRESSE_IP_PUBLIQUE:5000
```

Vous pouvez aussi tester :

```text
http://ADRESSE_IP_PUBLIQUE:5000/health
```

et :

```text
http://ADRESSE_IP_PUBLIQUE:5000/hello/Alice
```

## 10. Tester le redémarrage automatique

Redémarrez l'instance :

```bash
sudo reboot
```

Attendez que l'instance soit de nouveau disponible, reconnectez-vous en SSH puis vérifiez :

```bash
sudo systemctl status mon-api
```

L'API doit avoir redémarré automatiquement.

## 11. Commandes utiles

Voir les logs du service :

```bash
sudo journalctl -u mon-api
```

Suivre les logs en temps réel :

```bash
sudo journalctl -u mon-api -f
```

Redémarrer l'API :

```bash
sudo systemctl restart mon-api
```

Arrêter l'API :

```bash
sudo systemctl stop mon-api
```

## Remarque

Cette application Flask est volontairement simple et destinée à un TP pédagogique. Elle permet de manipuler EC2, SSH, Git, Python, les Security Groups et systemd.
 