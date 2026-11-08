# Recherche de podcasts – version à mise à jour automatique

Chaque jour, un robot GitHub télécharge le flux de Pierre-Emmanuel Barré et met à jour `data/barre.json`.
La page lit ce fichier (même site, donc pas de blocage du navigateur) : les nouveaux épisodes apparaissent tout seuls.

## Mise en place (une seule fois, environ 10 minutes)

1. Crée un compte gratuit sur **github.com**.
2. Clique sur **New repository**, donne un nom (ex. `podcasts`), choisis **Public**, puis **Create repository**.
3. Clique sur **uploading an existing file**, glisse-y **tout le contenu de ce dossier** (y compris le dossier caché `.github`), puis **Commit changes**.
   - Sur Mac, `Cmd + Maj + .` affiche les dossiers cachés. Si `.github` pose problème : **Add file > Create new file**, tape `.github/workflows/update.yml` comme nom et colles-y le contenu du fichier.
4. **Settings > Pages** : *Source* = **Deploy from a branch**, branche **main**, dossier **/ (root)**, puis **Save**.
5. **Settings > Actions > General > Workflow permissions** : choisis **Read and write permissions**, puis **Save**.
6. Onglet **Actions** > « Mise à jour des podcasts » > **Run workflow**. Attends environ une minute : `data/barre.json` se remplit.
7. Ouvre ton site : `https://TON-PSEUDO.github.io/NOM-DU-DEPOT/`

Ensuite, plus rien à faire. Si un jour les nouveautés cessent d'arriver, GitHub a peut-être mis la tâche en pause (dépôt inactif depuis 60 jours) : relance-la avec **Run workflow**.
