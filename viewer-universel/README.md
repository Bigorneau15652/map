# Viewer Universel — Widget Grist (DXF · PDF · 360°)

Visionneuse multi-format pour [Grist](https://www.getgrist.com), pensée pour un
**SI patrimoine** (sites → bâtiments → étages → pièces → portes). En sélectionnant
une ligne dans Grist, le widget ouvre le bon fichier et — pour les plans — **zoome
sur la pièce** correspondante.

> Widget statique (un seul `index.html`), hébergé sur GitHub Pages. Aucune
> dépendance payante, aucun serveur à maintenir.

---

## 1. Formats supportés

| Format | Moteur | Usage |
|---|---|---|
| **DXF** | parseur + Canvas maison | plans d'étage (1 fichier par étage) |
| **PDF** | PDF.js | documents, plans PDF |
| **Image 360°** | Pannellum | visites panoramiques |
| Image (jpg/png…) | `<img>` | photos |

### ⚠️ DWG → DXF (à lire avant tout)

Le **DWG** est un format binaire propriétaire Autodesk : **aucun navigateur ne sait
le lire**. Le widget travaille donc en **DXF** (format texte, ouvert). Deux façons
de produire vos DXF, **1 fichier par étage** comme vos DWG :

1. **Depuis votre logiciel CAO** : `Fichier > Enregistrer sous… > DXF` (R2013+ ASCII).
2. **Conversion en lot** (gratuite) : *ODA File Converter*
   (https://www.opendesign.com/guestfiles/oda_file_converter) — glissez vos DWG,
   sortie en DXF. Idéal pour convertir tous les étages d'un coup.

Stockez ensuite les `.dxf` sur le drive Nextcloud.

---

## 2. Préparer les plans DXF

Pour que le **zoom sur la pièce** fonctionne, le DXF doit respecter 2 règles :

1. **Chaque pièce = une polyligne FERMÉE** (`LWPOLYLINE` ou `POLYLINE` fermée).
2. **Un calque dédié contient le numéro de salle** (entités `TEXT`/`MTEXT`),
   placé *à l'intérieur* de la polyligne de la pièce.

Le widget associe automatiquement chaque numéro de salle à la polyligne qui
l'englobe (test point-dans-polygone). Le numéro de salle doit **correspondre à
l'identifiant de la pièce dans Grist** (la comparaison ignore espaces et casse :
` a101 ` ↔ `A101`).

---

## 3. Accès aux fichiers (Nextcloud)

Le widget télécharge les fichiers depuis le navigateur : utilisez des
**liens de partage publics** Nextcloud, terminés par `/download`.

```
https://votre-drive/s/XXXXXXXX/download
```

Un fichier protégé par login déclenchera une erreur « CORS / Failed to fetch ».
Si l'URL n'a pas d'extension (`…/download`), forcez le format dans ⚙ Config.

---

## 4. Configurer le widget dans Grist

1. Ajoutez un **Widget personnalisé**, URL :
   `https://bigorneau15652.github.io/map/viewer-universel/index.html`
2. Accès : **Lire la table**.
3. Ouvrez **⚙ Config** et renseignez :

| Champ | Rôle |
|---|---|
| **Colonne URL du fichier** *(requis)* | lien du DXF/PDF/image (souvent le plan d'étage) |
| **Colonne ID Pièce** *(option)* | identifiant de la pièce → zoom. Vide = vue étage globale |
| **Calque des IDs de salles** *(option)* | calque portant les n° de salle (sélectionnable après chargement d'un DXF) |
| **Colonne Nom Pièce** *(option)* | affiché dans l'infobulle |
| **Format de fichier** | `auto` ou forcé (utile pour les URLs `…/download`) |

---

## 5. Les deux modes d'usage

- **Vue étage** : sélectionnez un étage (colonne ID Pièce vide ou pièce absente du
  plan) → le plan s'affiche **entièrement** (ajusté à l'écran).
- **Vue pièce** : sélectionnez une pièce → le plan s'ouvre **zoomé sur la pièce**,
  la polyligne est surlignée. Bouton **◎ Pièce** pour recentrer, **⊡ Ajuster**
  pour revenir à l'étage entier.

Le **panneau Calques** (gauche) permet d'afficher/masquer chaque calque
individuellement (👁 / 🚫), ou tout afficher / tout masquer.

---

## 6. Modèle Grist conseillé (SI patrimoine)

Une table par niveau, reliées par les widgets liés de Grist
(*Sélectionner par*). La table **Pièces** porte au minimum :

| Colonne | Exemple | Usage widget |
|---|---|---|
| `id_piece` | `A101` | **ID Pièce** (doit matcher le texte DXF) |
| `nom` | `Bureau 101` | **Nom Pièce** |
| `plan_dxf` | `https://…/s/abcd/download` | **URL du fichier** (DXF de l'étage) |

Toutes les pièces d'un même étage pointent vers **le même DXF** (le plan de
l'étage) ; seul `id_piece` change le zoom.

---

## Limites connues

- DXF ASCII uniquement (pas de DWG natif — voir §1).
- Rendu 2D des entités courantes : `LINE`, `LWPOLYLINE`/`POLYLINE`, `CIRCLE`,
  `ARC`, `TEXT`, `MTEXT`. Les blocs `INSERT` ne sont pas développés.
- Les hachures (`HATCH`) et splines ne sont pas rendues.
</content>
</invoke>
