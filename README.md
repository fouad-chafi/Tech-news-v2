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

**[📸 SCREENSHOT À AJOUTER ICI : Vue complète du dashboard avec grilles d'articles]**
*Emplacement : `screenshots/dashboard-full-view.png`*

**Description :** Le dashboard affiche une grille responsive d'articles avec :
- **Header** avec barre de recherche
- **Filtres par catégories** colorés
- **Cartes articles** avec images, titres, métadonnées
- **Pagination** en bas de page

---

### 📱 Carte Article

**[📸 SCREENSHOT À AJOUTER ICI : Détail d'une carte article avec toutes ses informations]**
*Emplacement : `screenshots/article-card-detail.png`*

**Composants visibles :**
- Image de l'article (avec fallback si manquante)
- Titre et description tronquée
- **Score de pertinence** (1-5 étoiles)
- **Tags catégories** colorés
- Source et date de publication
- Effet hover pour interactivité

---

### 🔍 Filtres par Catégories

**[📸 SCREENSHOT À AJOUTER ICI : Section des filtres catégories avec tags cliquables]**
*Emplacement : `screenshots/category-filters.png`*

**Fonctionnalités :**
- Tags cliquables pour chaque catégorie
- Dénombrement d'articles par catégorie
- Couleurs uniques par catégorie
- Sélection multiple possible
- Reset rapide des filtres

---

### 📱 Version Mobile

**[📸 SCREENSHOT À AJOUTER ICI : Interface responsive sur smartphone]**
*Emplacement : `screenshots/mobile-responsive-view.png`*

**Adaptations mobiles :**
- Navigation simplifiée
- Cartes empilées verticalement
- Menu hamburger pour filtres
- Pagination condensée
- Interactions tactiles optimisées

---

### 🌙 Thème Sombre Professionnel

**[📸 SCREENSHOT À AJOUTER ICI : Palette de couleurs et thème sombre]**
*Emplacement : `screenshots/dark-theme-showcase.png`*

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

**[📸 SCREENSHOT À AJOUTER ICI : Schema ERD dans Supabase]**
*Emplacement : `screenshots/supabase-schema-erd.png`*

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

**[📸 SCREENSHOT À AJOUTER ICI : Table Editor Supabase]**
*Emplacement : `screenshots/supabase-table-editor.png`*

**Actions possibles :**
- Visualiser les données en temps réel
- Éditer manuellement si besoin
- Voir les relations entre tables
- Filtrer et rechercher

**[📸 SCREENSHOT À AJOUTER ICI : Vue des articles avec colonnes]**
*Emplacement : `screenshots/supabase-articles-view.png`*

---

### 📈 Statistiques en Temps Réel

**[📸 SCREENSHOT À AJOUTER ICI : Vue SQL Editor avec requêtes statistiques]**
*Emplacement : `screenshots/supabase-sql-stats.png`*

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

**[📸 SCREENSHOT À AJOUTER ICI : Menu principal Rich avec bordures]**
*Emplacement : `screenshots/cli-main-menu.png`*

```bash
╔═════════════════════════════════════════╗
║     Tech News Aggregator v2.0           ║
║   RSS → AI Analysis → Dashboard        ║
╚═════════════════════════════════════════╝
```

---

### 📂 Sélection des Sources

**[📸 SCREENSHOT À AJOUTER ICI : Menu sélection des groupes de sources]**
*Emplacement : `screenshots/cli-source-selection.png`*

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

**[📸 SCREENSHOT À AJOUTER ICI : Menu configuration max articles]**
*Emplacement : `screenshots/cli-max-articles-config.png`*

```bash
Configure maximum articles per source:
This limits how many articles to fetch from each RSS feed

Maximum articles per source [5/10/20/50] (10): 5
```

---

### 📊 Barre de Progression

**[📸 SCREENSHOT À AJOUTER ICI : Progression pendant le traitement]**
*Emplacement : `screenshots/cli-progress-bar.png`*

```bash
╭──────────────────────────────────────────────────────────────────╮
│ Processing 24 sources... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  42% │
╰──────────────────────────────────────────────────────────────────╯

⠙ Processing r/MachineLearning...
Fetching: https://www.reddit.com/r/MachineLearning/.json
Analyzing: "New optimization technique for..."
Filtering: [D] Self-Promotion Thread → FILTERED
Storing: ✅ "GPT-4 for code generation..."
```

---

### 📈 Rapport Final de Traitement

**[📸 SCREENSHOT À AJOUTER ICI : Tableau final Rich avec statistiques]**
*Emplacement : `screenshots/cli-processing-results.png`*

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

**[📸 SCREENSHOT À AJOUTER ICI : Dashboard avec nouveaux articles]**
*Emplacement : `screenshots/dashboard-with-new-articles.png`*

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

## 📞 Support & Ressources

- **Documentation complète** : [docs/](docs/)
- **Guide architecture** : [docs/Architecture.md](docs/Architecture.md)
- **Guide contribution** : [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues GitHub** : Signaler bugs et demander des features

---

**Made with ❤️ for developers by developers**

*Tech News Aggregator v2.0 - Votre flux d'actualités tech intelligent*