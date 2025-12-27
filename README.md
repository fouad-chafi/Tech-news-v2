# 🚀 Tech News Aggregator

**Système intelligent d'agrégation de news technologiques avec analyse IA locale**

---

## 📋 Table des Matières

1. [Présentation du Projet](#-présentation-du-projet)
2. [Dashboard Frontend](#-dashboard-frontend)
3. [Base de Données](#-base-de-données)
4. [Backend & CLI](#-backend--cli)
5. [Installation Rapide](#-installation-rapide)
6. [Utilisation Quotidienne](#-utilisation-quotidienne)

---

## 🎯 Présentation du Projet

Tech News Aggregator est un système automatisé qui collecte, analyse et présente les news technologiques les plus pertinentes pour les développeurs et ingénieurs IT.

### 🌟 Fonctionnalités Principales

| Fonctionnalité | Description |
|---------------|-------------|
| **🤖 Analyse IA** | Catégorisation automatique par LLM local |
| **📊 100+ Sources** | Blogs tech, médias Reddit, podcasts |
| **🎯 Filtrage Intelligent** | Élimine pubs, spam, contenu non-tech |
| **🌙 Dashboard Web** | Interface moderne et responsive |
| **⚡ Performance** | Processing rapide avec déduplication |

### 🔄 Workflow Global

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   100+ Sources   │───▶│  Analyse LLM    │───▶│  Base de Données│
│   RSS / Reddit   │    │  qwen2.5-7b     │    │   Supabase      │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  Dashboard Web  │
                                              │  Next.js 16     │
                                              └─────────────────┘
```

---

## 🎨 Dashboard Frontend

### 🖥️ Vue d'Ensemble du Dashboard

<img width="2112" height="1213" alt="image" src="https://github.com/user-attachments/assets/943df72f-acf1-4cd4-a76e-211587d17c8a" />


**Description :** Le dashboard affiche une grille responsive d'articles avec :
- **Header** avec barre de recherche
- **Filtres par catégories** colorés
- **Cartes articles** avec images, titres, métadonnées
- **Pagination** en bas de page

---

### 📱 Carte Article

<img width="1563" height="527" alt="image" src="https://github.com/user-attachments/assets/4a7b24e1-3bfd-4e4c-9fea-85bf9764f245" />


**Composants visibles :**
- Image de l'article (avec fallback si manquante)
- Titre et description tronquée
- **Score de pertinence** (1-5 étoiles)
- **Tags catégories** colorés
- Source et date de publication
- Effet hover pour interactivité

---

### 🔍 Filtres par Catégories

<img width="1583" height="1224" alt="image" src="https://github.com/user-attachments/assets/a77f4d70-02cf-4594-84f6-4905b2038b4c" />


**Fonctionnalités :**
- Tags cliquables pour chaque catégorie
- Dénombrement d'articles par catégorie
- Couleurs uniques par catégorie
- Sélection multiple possible
- Reset rapide des filtres

---

### 📱 Version Mobile

<img width="933" height="1131" alt="image" src="https://github.com/user-attachments/assets/ca040fbb-0caa-4a43-965e-d3d5d976b2f0" />


**Adaptations mobiles :**
- Navigation simplifiée
- Cartes empilées verticalement
- Menu hamburger pour filtres
- Pagination condensée
- Interactions tactiles optimisées

---

### 🌙 Thème Sombre Professionnel

**Palette de couleurs :**
```css
--background-primary: #0f172a  /* Dark slate */
--surface-color: #1e293b        /* Lighter slate */
--accent-blue: #3b82f6          /* Primary actions */
--accent-green: #10b981         /* Success states */
--accent-amber: #f59e0b         /* Warnings */
```

---

## 🗄️ Base de Données

### 📊 Schéma Supabase

<img width="1560" height="924" alt="image" src="https://github.com/user-attachments/assets/8812d8e2-66b6-4227-9aa8-e00a5c62090b" />


**Tables principales :**

#### 1. **sources** - Configuration des sources RSS
```
┌─────────────────────────────────────────┐
│ id              UUID (PK)               │
│ name            TEXT (UNIQUE)           │
│ rss_url         TEXT                   │
│ source_group    TEXT                   │
│ enabled         BOOLEAN                │
│ max_articles    INTEGER                │
└─────────────────────────────────────────┘
```

#### 2. **articles** - Articles analysés
```
┌─────────────────────────────────────────┐
│ id              UUID (PK)               │
│ title           TEXT                   │
│ description     TEXT                   │
│ url             TEXT (UNIQUE)          │
│ image_url       TEXT                   │
│ source_id       UUID (FK)              │
│ published_date  TIMESTAMP              │
│ relevance_score INTEGER (1-5)          │
│ tone            TEXT                   │
│ filtered        BOOLEAN                │
│ filter_reason   TEXT                   │
└─────────────────────────────────────────┘
```

#### 3. **categories** - Catégories dynamiques
```
┌─────────────────────────────────────────┐
│ id              UUID (PK)               │
│ name            TEXT (UNIQUE)           │
└─────────────────────────────────────────┘
```

#### 4. **article_categories** - Relation many-to-many
```
┌─────────────────────────────────────────┐
│ article_id      UUID (FK)              │
│ category_id     UUID (FK)              │
└─────────────────────────────────────────┘
```

---

### 🔍 Interface Supabase
<img width="2452" height="756" alt="image" src="https://github.com/user-attachments/assets/26dd50e8-8163-4762-a2b2-dc2fb1bdc167" />

**Actions possibles :**
- Visualiser les données en temps réel
- Éditer manuellement si besoin
- Voir les relations entre tables
- Filtrer et rechercher


---

### 📈 Statistiques en Temps Réel

**Requêtes utiles :**
```sql
-- Articles par catégorie
SELECT c.name, COUNT(ac.article_id) as count
FROM categories c
LEFT JOIN article_categories ac ON c.id = ac.category_id
GROUP BY c.name
ORDER BY count DESC;

-- Top sources
SELECT s.name, COUNT(a.id) as article_count
FROM sources s
LEFT JOIN articles a ON s.id = a.source_id
WHERE a.filtered = false
GROUP BY s.name
ORDER BY article_count DESC;
```

---

## ⚙️ Backend & CLI

### 🖥️ Interface CLI Principale

<img width="1504" height="1079" alt="image" src="https://github.com/user-attachments/assets/25f4146d-50c1-4c04-b812-387bddc80671" />


```bash
╔═════════════════════════════════════════╗
║     Tech News Aggregator v2.0           ║
║   RSS → AI Analysis → Dashboard        ║
╚═════════════════════════════════════════╝
```

---

### 📂 Sélection des Sources

```bash
Select source groups to process:
Enter group numbers separated by commas (e.g., 1,3,5) or 'all' for all groups

[ 1] AI_ML (10/10 enabled)        ✓
[ 2] DEV_GENERAL (7/7 enabled)    ✓
[ 3] WEB_DEV (7/7 enabled)        ✓
[ 4] MOBILE_DEV (3/3 enabled)      ✓
[ 5] DEVOPS_CLOUD (7/7 enabled)    ✓
[ 6] CYBERSECURITY (5/5 enabled)   ✓
[ 7] STARTUPS (6/6 enabled)        ✓
[ 8] REDDIT_TECH (8/8 enabled)     ✓
[ 9] NEWS_MAINSTREAM (7/7 enabled) ✓

Your selection: 1,3,8
```

---

### ⚙️ Configuration Articles par Source


```bash
Configure maximum articles per source:
This limits how many articles to fetch from each RSS feed

Maximum articles per source [5/10/20/50] (10): 5
```

---

### 📊 Barre de Progression

<img width="1898" height="1017" alt="image" src="https://github.com/user-attachments/assets/059fd3ec-76dd-4f9e-ad65-c1e18e95b470" />


```bash
╭──────────────────────────────────────────────────────────────────╮
│ Processing 24 sources... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  42% │
╰──────────────────────────────────────────────────────────────────╯

⠙ Processing r/MachineLearning...
Fetching: https://www.reddit.com/r/MachineLearning/.json
Analyzing: "New optimization technique for..."
Filtering: [D] Self-Promotion Thread → FILTERED
```

---

### 📈 Rapport Final de Traitement

```bash
╭───────────────────────┬─────────╮
│ Metric                │  Value  │
├───────────────────────┼─────────┤
│ Sources Processed     │   24    │
│ Articles Found        │   120   │
│ Articles Analyzed     │   118   │
│ Articles Stored       │   115   │
│ Articles Filtered     │     3   │
│ New Categories        │     2   │
│ Errors Encountered    │     0   │
╰───────────────────────┴─────────╯
```

---

### 🧪 Tests de Filtrage

**[📸 SCREENSHOT À AJOUTER ICI : Résultats test_filtering.py]**
*Emplacement : `screenshots/test-filtering-results.png`*

```bash
$ python test_filtering.py

╔════════════════════════════════════════════════════════════╗
║                    TESTING ARTICLE FILTERING                  ║
╚════════════════════════════════════════════════════════════╝

Test Article 1: "[D] Self-Promotion Thread"
Expected: FILTERED | Actual: FILTERED ✅
Reason: Reddit self-promotion thread

Test Article 2: "Python 3.12 Performance Improvements"
Expected: ACCEPTED | Actual: ACCEPTED ✅
Categories: DEV, TOOLS, WEB
```

---

## 🚀 Installation Rapide

### ⚡ Quick Start (5 minutes)

#### 1. Cloner le Projet

```bash
git clone https://github.com/your-repo/Tech-news-v2.git
cd Tech-news-v2
```

#### 2. Backend Python

```bash
# Environment virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos clés Supabase
```

#### 3. Frontend Next.js

```bash
cd tech-news-dashboard
npm install
```

#### 4. Base de Données

```bash
# Depuis la racine du projet
python scripts/setup_database.py
python scripts/populate_sources.py
```

#### 5. Démarrer

**Terminal 1 - Backend :**
```bash
python main.py
```

**Terminal 2 - Frontend :**
```bash
cd tech-news-dashboard
npm run dev
```

**Accéder au dashboard :** `http://localhost:3000`

---

## 💡 Utilisation Quotidienne

### 🔄 Lancer une Collecte de News

```bash
$ python main.py

╔══════════════════════════════════════════════╗
║   🔍 Tech News Aggregator v2.0               ║
║   Collecte et analyse les news tech          ║
╚══════════════════════════════════════════════╝

✅ Connected to Supabase
✅ Connected to Local LLM
✅ Loaded 60 RSS sources

Select source groups to process:
[1] All sources
[2] Tech blogs only
[3] Reddit only

Your choice: 1

Processing...
✨ 127 articles found
🤖 Analyzing with LLM...
📊 125 articles stored
❌ 2 articles filtered (non-tech content)

Done! Check your dashboard at http://localhost:3000
```

---

### 📊 Consulter le Dashboard

1. **Ouvrir** `http://localhost:3000`
2. **Explorer** les articles par catégorie
3. **Filtrer** par mots-clés
4. **Cliquer** sur un article pour le lire

---

### 🔍 Vérifier la Base de Données

```bash
$ python scripts/check_database.py

╔══════════════════════════════════════════════╗
║         Database Statistics                  ║
╠══════════════════════════════════════════════╣
║ Total Articles:     127                       ║
║ Active Articles:    125                       ║
║ Filtered Articles:  2                         ║
║ Categories:         21                        ║
║ Sources:            60                        ║
╚══════════════════════════════════════════════╝
```

---

### 🧪 Tester le Filtrage

```bash
$ python test_filtering.py

Testing improved filtering rules...
✅ Reddit self-promotion threads → FILTERED
✅ Biology articles → FILTERED
✅ Tech articles → ACCEPTED
```

---

## 📚 Emplacements des Screenshots

Pour compléter ce README, ajoutez vos screenshots dans :

```
Tech-news-v2/
├── screenshots/
│   ├── dashboard-full-view.png         ⬅️ Vue complète dashboard
│   ├── article-card-detail.png         ⬅️ Détail carte article
│   ├── category-filters.png            ⬅️ Filtres catégories
│   ├── mobile-responsive-view.png     ⬅️ Version mobile
│   ├── dark-theme-showcase.png         ⬅️ Thème sombre
│   ├── supabase-schema-erd.png         ⬅️ Schema base de données
│   ├── supabase-table-editor.png       ⬅️ Interface Supabase
│   ├── supabase-articles-view.png      ⬅️ Vue articles Supabase
│   ├── supabase-sql-stats.png          ⬅️ Requêtes statistiques
│   ├── cli-main-menu.png               ⬅️ Menu CLI principal
│   ├── cli-source-selection.png       ⬅️ Sélection sources
│   ├── cli-max-articles-config.png     ⬅️ Configuration max articles
│   ├── cli-progress-bar.png            ⬅️ Barre progression
│   ├── cli-processing-results.png      ⬅️ Résultats finaux
│   ├── test-filtering-results.png      ⬅️ Tests filtrage
│   └── dashboard-with-new-articles.png ⬅️ Dashboard avec nouveaux articles
```

**Conseils pour les screenshots :**
- Utiliser un thème sombre cohérent
- Afficher les données réelles de la base
- Capturer en haute résolution (1920x1080 minimum)
- Garder les interfaces professionnelles
- Montrer des fonctionnalités clés

---

## 🎯 Prochaines Étapes

### Pour Commencer
1. ✅ Installer les dépendances
2. ✅ Configurer la base de données
3. ✅ Lancer la première collecte
4. ✅ Explorer le dashboard
5. ✅ Ajuster les filtres si nécessaire

### Pour Personnaliser
- **Ajouter des sources** → Éditer `sources.json`
- **Ajuster le filtrage** → Modifier `modules/llm_analyzer.py`
- **Changer le thème** → Modifier `tech-news-dashboard/src/app/globals.css`
- **Ajouter des catégories** → Laisser le LLM les créer automatiquement

---


*Tech News Aggregator v2.0 - Votre flux d'actualités tech intelligent*
