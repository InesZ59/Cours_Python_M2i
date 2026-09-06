# Lab GKE Pods et Services

## Objectif
Déployer une application web simple avec des images publiques qui fonctionnent vraiment.

---

## Étape 1 : Préparer le cluster

```bash
# Vérifier
kubectl get nodes
```
```bash
NAME                    STATUS   ROLES           AGE     VERSION
desktop-control-plane   Ready    control-plane   4h18m   v1.36.1
```cd

## Étape 2 : Déployer Nginx (serveur web)

### 2.1 Pod Nginx
```yaml
# nginx-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```
````bash
kubectl apply -f nginx-pod.yaml
==> pod/web-server created

Vérifier
kubectl get pods
kubectl describe pod web-server
kubectl logs web-server
```
### 2.2 Service Nginx (externe)
```yaml

#nano nginx-service.yaml
# nginx-service.yaml
apiVersion: v1kubectl 
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

**Déployer :**
```bash
kubectl apply -f nginx-pod.yaml
# pod/web-server created
kubectl apply -f nginx-service.yaml
# clearservice/web-service created
```
---

## Étape 3 : Déployer Apache (autre serveur web)

### 3.1 Pod Apache
```yaml
# apache-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: apache-server
  labels:
    app: apache
spec:
  containers:
  - name: apache
    image: httpd:latest
    ports:
    - containerPort: 80
```

### 3.2 Service Apache (externe)
```yaml
# apache-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: apache-service
spec:
  selector:
    app: apache
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

**Déployer :**
```bash
kubectl apply -f apache-pod.yaml
kubectl apply -f apache-service.yaml
```

---

## Étape 4 : Déployer WordPress + MySQL

### 4.1 Pod MySQL
```yaml
# mysql-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql-db
  labels:
    app: mysql
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    ports:
    - containerPort: 3306
    env:
    - name: MYSQL_ROOT_PASSWORD
      value: "motdepasse123"
    - name: MYSQL_DATABASE
      value: "wordpress"
    - name: MYSQL_USER
      value: "wpuser"
    - name: MYSQL_PASSWORD
      value: "wppass"
```

### 4.2 Service MySQL (interne seulement)
```yaml
# mysql-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
```

### 4.3 Pod WordPress
```yaml
# wordpress-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: wordpress-site
  labels:
    app: wordpress
spec:
  containers:
  - name: wordpress
    image: wordpress:latest
    ports:
    - containerPort: 80
    env:
    - name: WORDPRESS_DB_HOST
      value: "mysql-service:3306"
    - name: WORDPRESS_DB_NAME
      value: "wordpress"
    - name: WORDPRESS_DB_USER
      value: "wpuser"
    - name: WORDPRESS_DB_PASSWORD
      value: "wppass"
```

### 4.4 Service WordPress (externe)
```yaml
# wordpress-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress-service
spec:
  selector:
    app: wordpress
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

**Déployer :**
```bash
kubectl apply -f mysql-pod.yaml
kubectl apply -f mysql-service.yaml
kubectl apply -f wordpress-pod.yaml
kubectl apply -f wordpress-service.yaml
```

---

## Étape 5 : Vérifier et tester

### 5.1 Voir tous les pods et services
```bash
kubectl get pods
#NAME                      READY   STATUS    RESTARTS   AGE
apache-server             1/1     Running   0          3m38s
my-app-57f9cc845b-49h52   1/1     Running   0          5h21m
mysql-db                  1/1     Running   0          39s
web-server                1/1     Running   0          3h48m
wordpress-site            1/1     Running   0          20s

kubectl get services
#NAME                TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
apache-service      LoadBalancer   10.96.197.32   <pending>     80:31666/TCP   3m42s
kubernetes          ClusterIP      10.96.0.1      <none>        443/TCP        5h26m
mysql-service       ClusterIP      10.96.7.225    <none>        3306/TCP       43s
web-service         LoadBalancer   10.96.104.85   172.19.0.5    80:31640/TCP   34m
wordpress-service   LoadBalancer   10.96.25.82    <pending>     80:31484/TCP   24s

```

### 5.2 Attendre les IP externes
```bash
# Surveiller les services LoadBalancer
kubectl get services --watch
#NAME                TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
apache-service      LoadBalancer   10.96.197.32   <pending>     80:31666/TCP   6m56s
kubernetes          ClusterIP      10.96.0.1      <none>        443/TCP        5h29m
mysql-service       ClusterIP      10.96.7.225    <none>        3306/TCP       3m57s
web-service         LoadBalancer   10.96.104.85   172.19.0.5    80:31640/TCP   38m
wordpress-service   LoadBalancer   10.96.25.82    <pending>     80:31484/TCP   3m38s

# Ou vérifier périodiquement
kubectl get service web-service
#NAME          TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-service   LoadBalancer   10.96.104.85   172.19.0.5    80:31640/TCP   39m

kubectl get service apache-service
#NAME             TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
apache-service   LoadBalancer   10.96.197.32   <pending>     80:31666/TCP   8m20s

kubectl get service wordpress-service
#NAME                TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
wordpress-service   LoadBalancer   10.96.25.82   <pending>     80:31484/TCP   5m27s
```

### 5.3 Accéder aux applications
```bash
# Obtenir les URLs
echo "Nginx: http://$(kubectl get service web-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
# Nginx: http://172.19.0.5 ==> ne fonctionne pas 
echo "Apache: http://$(kubectl get service apache-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
# Apache: http:// pas d'adresse IP 
kubectl get services --watch ==> status "pending"
echo "WordPress: http://$(kubectl get service wordpress-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
# WordPress: http://
kubectl get services --watch ==> status "pending"
```

---

## Étape 6 : Tests de connectivité

### 6.1 Tester la communication interne
```bash
# Créer un pod temporaire
kubectl run test-pod --image=busybox --rm -it --restart=Never -- /bin/sh
comment cela fonctionne?

# Dans le pod de test :
# nslookup mysql-service
# nslookup web-service
# wget -qO- web-service
```

### 6.2 Examiner les pods
```bash
# Logs des pods
kubectl logs web-server ==> OK
kubectl logs mysql-db ==> OK
kubectl logs wordpress-site ==> OK

# Détails d'un pod
kubectl describe pod wordpress-site ==> OK

# Entrer dans un pod
kubectl exec -it web-server -- /bin/bash
#error: Internal error occurred: Internal error occurred: error executing command in container: failed to exec in container: failed to start exec "af2a90629cc608c3554f20724f632a4f06bc7799c1f4f85c4a55557faa2cf8b5": OCI runtime exec failed: exec failed: unable to start container process: exec: "C:/Program Files/Git/usr/bin/bash": stat C:/Program Files/Git/usr/bin/bash: no such file or directory
```

---

## Étape 7 : Explorer les services

### 7.1 Types de services
```bash
# ClusterIP (interne seulement)
kubectl get service mysql-service
#NAME            TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
mysql-service   ClusterIP   10.96.7.225   <none>        3306/TCP   71m

# LoadBalancer (externe)
kubectl get service wordpress-service
#NAME                TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
wordpress-service   LoadBalancer   10.96.25.82   <pending>     80:31484/TCP   71m
# Voir les endpoints
kubectl get endpoints
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
#NAME                ENDPOINTS         AGE
apache-service      10.244.0.7:80     74m
kubernetes          172.19.0.2:6443   6h37m
mysql-service       10.244.0.8:3306   71m
web-service         10.244.0.6:80     106m
wordpress-service   10.244.0.9:80     71m
```

### 7.2 Détails des services
```bash
kubectl describe service wordpress-service ==> OK
kubectl describe service mysql-service
#Name:                     mysql-service
Namespace:                default
Labels:                   <none>
Annotations:              <none>
Selector:                 app=mysql
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.7.225
IPs:                      10.96.7.225
Port:                     <unset>  3306/TCP
TargetPort:               3306/TCP
Endpoints:                10.244.0.8:3306
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
```

---

## Nettoyage

```bash
# Supprimer tous les objets
kubectl delete pod --all
kubectl delete service --all
