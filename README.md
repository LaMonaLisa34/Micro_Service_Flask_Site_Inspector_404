# 📘 Micro_Service_Flask_Site_Inspector_404

## Description

**`site_inspector_404_flask`** est un micro-service Python/Flask conçu pour **enquêter sur les erreurs 404** détectées par un crawler.  
Il fonctionne en architecture **event-driven** grâce à **Kafka** :  

- Le **crawler** envoie chaque URL en erreur 404 dans un **topic Kafka** (`urls_404`).  
- L’**inspector** consomme ces messages, les stocke, applique des règles d’analyse (slash manquant, casse, locale FR/EN, etc.) et expose :  
- Une **API REST** pour interroger les résultats.  
- Des **métriques Prometheus** pour intégration avec Grafana.  

L’objectif est d’identifier rapidement où se trouvent les erreurs 404 (liens internes cassés, referrers externes, trafic de bots, routes obsolètes) afin de permettre une correction ciblée dans le site ou ses contenus.

---

## Architecture

```
[Crawler] → (Kafka topic: urls_404) → [Inspector] → /metrics → [Prometheus] → [Grafana]
```

- **Crawler** : explore les URLs et publie les erreurs 404 dans Kafka.  
- **Inspector** : consomme le topic `urls_404`, analyse et expose les résultats.  
- **Prometheus** : scrappe `/metrics` de l’inspector.  
- **Grafana** : visualise les stats (top 404, referrers, patterns).  

---

## Fonctionnalités

- 🔎 **Ingestion** des erreurs 404 depuis Kafka.  
- 🗃️ **Stockage** (Postgres/SQLite) pour historisation et analyse.  
- 📊 **Métriques Prometheus** (exposées sur `/metrics`).  
- 🌍 **API REST** :
  - `/api/404/top` → top des URLs en 404  
  - `/api/404/referrers` → top des referrers fautifs  
  - `/api/redirect-suggestions` → suggestions de redirection  
  
- 🧩 **Analyse** des patterns :  
  - Slash final manquant/ajouté  
  - Majuscules/minuscules  
  - Correspondance approximative (Levenshtein)  

---

## Démarrage rapide

### 1. Prérequis
- Python 3.10+  
- Docker & Docker Compose  
- Kafka (Zookeeper inclus dans Docker Compose)  

### 2. Cloner le projet
```bash
git clone https://github.com/LaMonaLisa34/Micro_Service_Flask_Site_Inspector_404.git
cd site_inspector_404_flask
```

### 3. Installer les dépendances (mode dev local)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Lancer le service Flask
```bash
python run.py
```

Accessible sur :  
- API : http://localhost:8000  
- Metrics Prometheus : http://localhost:8000/metrics  
- Healthcheck : http://localhost:8000/health  

---

## Exemple de message Kafka

Le crawler publie dans le topic `urls_404` un message JSON du type :  

```json
{
  "url": "https://example.com/foobar",
  "referrer": "https://example.com/foobar/bar",
  "status": 404,
  "timestamp": "2025-09-01T12:00:00Z",
  "user_agent": "MyCrawler/1.0"
}
```

---

## Exemple d’appel API

### Ingestion (si pas de Kafka)
```bash
curl -X POST http://localhost:8000/ingest   -H "Content-Type: application/json"   -d '{"path":"/fr/race/test","source":"crawler"}'
```

### Récupérer les métriques
```bash
curl http://localhost:8000/metrics
```
