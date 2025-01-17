# **Projet Sismiques 2024 — Visualisation & Analyse**

Ce projet propose un **dashboard interactif** pour explorer et analyser les séismes de 2024. Il offre :

- Un **histogramme** pour visualiser la distribution des magnitudes  
- Une **carte 2D (Mapbox)** pour afficher séismes et failles tectoniques  
- Un **globe 3D** (projection orthographique) pour examiner la répartition mondiale  
- Des **métriques** (nombre total de séismes, magnitude min/max, etc.)  

---

## 1. **User Guide**

1. **Prérequis**  
   - **Python ≥ 3.8**  
   - Modules listés dans [requirements.txt](requirements.txt)

2. **Installation**  
   ```bash
   # 1) Cloner le dépôt
   git clone https://github.com/aaAuguste/Data_python.git
   
   # 2) Installer les dépendances
   pip install -r requirements.txt
Mise à jour / Téléchargement des données

### Mise à jour / Téléchargement des données

1. **Modifiez les paramètres du script `get_data.py`** :  
   - **Plage de temps** : `start_time`, `end_time`  
   - **Magnitude minimale** : `min_magnitude`  

2. **Exécutez le script** :  
   ```bash
   python src/utils/get_data.py


3. **Exécutez** :
    
    ```bash
    python src/utils/get_data.py
    ```
Les données brutes sont placées dans data/raw/.

4. **Nettoyez les données** :

    ```bash
    python src/utils/clean_data.py`
    ```
Résultat : data/cleaned/earthquake_data_cleaned.csv.

5. **Lancer le dashboard** :
    ```bash
    python main.py
    Rendez-vous sur http://127.0.0.1:8051/ pour accéder au tableau de bord.
    ```
## 2. **Data**

1. **Sources**  
   - **Séismes** : [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/)  
   - **Failles tectoniques** : [Tectonic Plate Boundaries](https://github.com/fraxen/tectonicplates)

2. **Organisation**  
   - `data/raw/` : Données brutes CSV après téléchargement  
   - `data/cleaned/` : Données finalisées (`earthquake_data_cleaned.csv`)


## 3. **Developer Guide**

1. **Structure du projet**  
   ```bash
   
    DATA_PYTHON/
    │
    ├── data/                         
    │   ├── cleaned/                  
    │   │   └── earthquake_data_cleaned.csv
    │   ├── raw/                      
    │       └── earthquake_data.csv
    │
    ├── src/                          
    │   ├── assets/                   
    │   │   └── styles.css
    │   ├── components/               
    │   │   └── earthquake_visual_component.py
    │   ├── pages/                    
    │   │   └── home.py
    │   ├── utils/                    
    │       ├── clean_data.py         
    │       ├── common_functions.py   
    │       └── get_data.py           
    │
    ├── app.py                       
    ├── config.py                     
    ├── main.py                       
    ├── .gitignore                   
    ├── README.md                     
    └── requirements.txt              



### Ajouter une page ou un graphique

#### Nouvelle page

1. Créez `new_page.py` dans `src/pages/`.  
2. Définissez un layout :  
   ```python
   layout = html.Div([ ... ])
Importez la page dans app.layout.

Nouveau graphique :
    
Implémentez la fonction de génération dans `common_functions.py`.
Appelez cette fonction dans `earthquake_visual_component.py` dans la partie callback.

## 4. **Rapport d’Analyse**

### Distribution des magnitudes

- Un histogramme montre la répartition des séismes, il y a beaucoup plus de séisme
dans les magnitudes moins  élevées

### Activité tectonique

- Forte concentration sur la **Ceinture de Feu du Pacifique**.
- Les failles majeures (**dorsales océaniques**, **fosses**) présentent un pic d’activité.

### Vue 3D

- Met en évidence les **zones ressenties** en survolant un séisme.
- Visualisation globale de la répartition planétaire.

### Conclusion

- L’analyse confirme la **corrélation entre failles tectoniques et intensité sismique**.
- Les zones à risque (2024) se situent principalement autour des frontières de plaques.

---

## 5. **Copyright**

Je déclare sur l’honneur que le code fourni a été produit par nous-mêmes, à l’exception des éléments suivants :

- **Données tectoniques** : issues de [fraxen/tectonicplates](https://github.com/fraxen/tectonicplates).  
- **API USGS** : utilisée pour collecter les données sismiques.

  





