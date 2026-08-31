#!/usr/bin/env bash
#
# Migration des widgets Grist vers l'organisation GitHub de l'UMPV.
#
# Pour chaque dépôt source :
#   1. clone de la dernière version (sans l'historique),
#   2. réécriture des URL bigorneau15652.github.io / github.com/Bigorneau15652
#      vers la nouvelle organisation,
#   3. injection d'un <meta name="robots" content="noindex, nofollow"> dans
#      chaque page HTML (widgets « discrets », non référencés par Google),
#   4. neutralisation des workflows GitHub Actions hérités (release / publish
#      npm) qui échoueraient sur la nouvelle organisation,
#   5. commit initial unique,
#   6. création du dépôt dans l'organisation + push (si la CLI `gh` est
#      disponible et authentifiée ; sinon le script s'arrête juste avant le
#      push et affiche la commande à lancer).
#
# Usage :
#   ./migrer-vers-umpv.sh --org NOM-DE-L-ORG [options]
#
# Options :
#   --org NOM             (obligatoire) organisation GitHub de destination.
#   --source-user NOM     compte source (défaut : Bigorneau15652).
#   --workdir CHEMIN      dossier de travail (défaut : dossier temporaire).
#   --branch NOM          branche par défaut des nouveaux dépôts (défaut : main).
#   --map-visibility V    public|private pour le dépôt `map` (défaut : public,
#                         car GitHub Pages n'est servi depuis un dépôt privé
#                         qu'avec un plan payant — voir README.md).
#   --only REPO[,REPO]    ne migrer que ces dépôts.
#   --keep-workflows      ne pas neutraliser .github/workflows.
#   --no-noindex          ne pas injecter la balise robots noindex.
#   --dry-run             tout préparer localement, ne rien créer ni pousser.
#   -h, --help            cette aide.

set -euo pipefail

ORG=""
SOURCE_USER="Bigorneau15652"
WORKDIR=""
BRANCH="main"
MAP_VISIBILITY="public"
ONLY=""
KEEP_WORKFLOWS=0
NOINDEX=1
DRY_RUN=0

die() { printf '\033[31mErreur :\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m→\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[33m!\033[0m %s\n' "$*"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --org)            ORG="${2:-}"; shift 2 ;;
    --source-user)    SOURCE_USER="${2:-}"; shift 2 ;;
    --workdir)        WORKDIR="${2:-}"; shift 2 ;;
    --branch)         BRANCH="${2:-}"; shift 2 ;;
    --map-visibility) MAP_VISIBILITY="${2:-}"; shift 2 ;;
    --only)           ONLY="${2:-}"; shift 2 ;;
    --keep-workflows) KEEP_WORKFLOWS=1; shift ;;
    --no-noindex)     NOINDEX=0; shift ;;
    --dry-run)        DRY_RUN=1; shift ;;
    -h|--help)        sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)                die "option inconnue : $1 (voir --help)" ;;
  esac
done

[ -n "$ORG" ] || die "--org est obligatoire. Exemple : --org univ-paul-valery"
case "$MAP_VISIBILITY" in public|private) ;; *) die "--map-visibility doit valoir public ou private" ;; esac
command -v git >/dev/null || die "git est introuvable."

# Dépôts à migrer : "nom:visibilité". Le dépôt `map` héberge les pages servies
# à Grist (GitHub Pages) ; les autres ne contiennent que du code/outillage et
# restent privés.
REPOS=(
  "map:${MAP_VISIBILITY}"
  "grist-energie-eau-sync:private"
  "eau-umpv-import:private"
  "carte-batiments-eau:private"
  "pv-umpv-import:private"
)

if [ -n "$ONLY" ]; then
  filtered=()
  for entry in "${REPOS[@]}"; do
    name="${entry%%:*}"
    case ",$ONLY," in *",$name,"*) filtered+=("$entry") ;; esac
  done
  [ ${#filtered[@]} -gt 0 ] || die "--only ne correspond à aucun dépôt connu."
  REPOS=("${filtered[@]}")
fi

if [ -z "$WORKDIR" ]; then
  WORKDIR="$(mktemp -d -t migration-umpv-XXXXXX)"
fi
mkdir -p "$WORKDIR"

HAVE_GH=0
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  HAVE_GH=1
else
  warn "CLI \`gh\` absente ou non authentifiée : les dépôts ne seront ni créés ni poussés automatiquement."
  warn "Chaque dépôt sera préparé localement et la commande de push vous sera affichée."
fi

info "Organisation cible : $ORG"
info "Dossier de travail : $WORKDIR"
[ "$DRY_RUN" = 1 ] && warn "MODE --dry-run : aucune écriture sur GitHub."
echo

SUMMARY=()

for entry in "${REPOS[@]}"; do
  repo="${entry%%:*}"
  visibility="${entry##*:}"
  src="https://github.com/${SOURCE_USER}/${repo}.git"
  dest="$WORKDIR/$repo"

  echo "──────────────────────────────────────────────"
  info "Dépôt : $repo (destination : $ORG/$repo, $visibility)"

  rm -rf "$dest"
  if ! git clone --depth 1 --quiet "$src" "$dest" 2>/dev/null; then
    warn "Clone impossible ($src). Dépôt privé ? Vérifiez vos identifiants git/gh, puis relancez avec --only $repo."
    SUMMARY+=("✗ $repo — clone échoué")
    continue
  fi
  ok "cloné (dernière version, sans historique)"

  rm -rf "$dest/.git"

  # 1. Réécriture des URL du compte personnel vers l'organisation.
  #    On ne touche qu'aux fichiers texte, en ignorant les binaires.
  changed=0
  while IFS= read -r -d '' f; do
    if grep -qi "bigorneau15652" "$f" 2>/dev/null; then
      perl -pi -e "
        s{\Q${SOURCE_USER}\E\.github\.io}{${ORG}.github.io}gi;
        s{github\.com/\Q${SOURCE_USER}\E}{github.com/${ORG}}gi;
        s{raw\.githack\.com/\Q${SOURCE_USER}\E}{raw.githack.com/${ORG}}gi;
        s{\@\Q${SOURCE_USER}\E/}{\@${ORG}/}gi;
      " "$f"
      changed=$((changed + 1))
    fi
  done < <(grep -rIlZi "bigorneau15652" "$dest" 2>/dev/null || true)
  [ "$changed" -gt 0 ] && ok "URL réécrites dans $changed fichier(s)" || info "aucune URL à réécrire"

  # 2. Balise noindex dans chaque page HTML (widgets discrets).
  if [ "$NOINDEX" = 1 ]; then
    n=0
    while IFS= read -r -d '' f; do
      grep -qi 'name="robots"' "$f" && continue
      grep -qi '<head' "$f" || continue
      perl -0pi -e 's{(<head[^>]*>)}{$1\n  <meta name="robots" content="noindex, nofollow">}i' "$f"
      n=$((n + 1))
    done < <(find "$dest" -type f -name '*.html' -print0)
    ok "noindex ajouté à $n page(s) HTML"
  fi

  # 3. Neutralisation des workflows hérités (release automatique, publication
  #    npm) : ils échoueraient sur la nouvelle organisation faute de secrets,
  #    et publieraient sous le mauvais compte. Réactivables en renommant le
  #    dossier.
  if [ "$KEEP_WORKFLOWS" = 0 ] && [ -d "$dest/.github/workflows" ]; then
    mv "$dest/.github/workflows" "$dest/.github/workflows-desactives"
    cat > "$dest/.github/workflows-desactives/LISEZMOI.md" <<'EOF'
# Workflows désactivés lors de la migration

Ces workflows venaient du dépôt d'origine (`gristlabs/grist-widget` puis le
compte personnel). Ils ont été désactivés pendant la migration :

- `release.yml` crée une release à chaque push sur la branche par défaut ;
- `publish-npm-package.yml` publie un paquet npm sous le compte d'origine ;
- `main.yml` lance la CI de test du dépôt amont.

Pour en réactiver un : déplacer le fichier dans `.github/workflows/` et
vérifier que les secrets nécessaires existent bien dans l'organisation.
EOF
    ok "workflows GitHub Actions neutralisés (.github/workflows-desactives/)"
  fi

  # 4. Commit initial unique.
  (
    cd "$dest"
    git init --quiet -b "$BRANCH"
    git add -A
    git -c user.name="Migration UMPV" -c user.email="noreply@univ-montp3.fr" \
        commit --quiet -m "Import initial des widgets Grist

Copie de la dernière version de ${SOURCE_USER}/${repo}, sans historique.
URL et références réécrites vers l'organisation ${ORG}."
  )
  ok "commit initial créé (branche $BRANCH)"

  # 5. Création + push.
  if [ "$DRY_RUN" = 1 ]; then
    SUMMARY+=("• $repo — préparé dans $dest (dry-run, non poussé)")
    continue
  fi

  if [ "$HAVE_GH" = 1 ]; then
    if gh repo view "$ORG/$repo" >/dev/null 2>&1; then
      warn "$ORG/$repo existe déjà — push ignoré, vérifiez manuellement."
      SUMMARY+=("! $repo — dépôt déjà existant, non poussé")
      continue
    fi
    gh repo create "$ORG/$repo" "--$visibility" --disable-wiki >/dev/null
    (
      cd "$dest"
      git remote add origin "https://github.com/$ORG/$repo.git"
      git push -u origin "$BRANCH" --quiet
    )
    ok "poussé vers https://github.com/$ORG/$repo ($visibility)"
    SUMMARY+=("✓ $repo — https://github.com/$ORG/$repo ($visibility)")
  else
    SUMMARY+=("• $repo — prêt dans $dest ; à pousser à la main")
    cat <<EOF

  Dépôt préparé. Créez « $repo » dans l'organisation $ORG en $visibility
  (sans README, sans .gitignore, sans licence), puis :

    cd "$dest"
    git remote add origin https://github.com/$ORG/$repo.git
    git push -u origin $BRANCH

EOF
  fi
done

echo
echo "──────────────────────────────────────────────"
echo "Récapitulatif :"
for line in "${SUMMARY[@]}"; do echo "  $line"; done
echo
echo "Étape suivante : activer GitHub Pages sur $ORG/map"
echo "  Settings → Pages → Source: Deploy from a branch → $BRANCH / (root)"
echo "puis mettre à jour les URL des widgets dans Grist"
echo "  (tableau de correspondance dans docs/migration-umpv/README.md)."
