/*
 * Relais CORS pour le drive UPV — à déployer sur Cloudflare Workers (gratuit).
 *
 * Rôle : le widget Grist ne peut pas lire un fichier hébergé sur un autre
 * domaine (le drive) car Nextcloud n'envoie pas l'en-tête CORS, et le lien
 * /download fait en plus une redirection 303 que le navigateur refuse en
 * cross-domaine. Ce relais récupère le fichier CÔTÉ SERVEUR (il suit la
 * redirection tout seul) et le renvoie au widget avec l'en-tête CORS.
 *
 * Usage depuis le widget (champ « Proxy CORS ») :
 *   https://VOTRE-WORKER.workers.dev/?url={url}
 *
 * Option : restreindre aux seuls fichiers du drive UPV (recommandé) en
 * gardant la vérification ALLOWED_HOST ci-dessous.
 */

const ALLOWED_HOST = 'upvdrive.univ-montp3.fr'; // mettre '' pour autoriser tout

export default {
  async fetch(request) {
    // Préflight CORS éventuel
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    const target = new URL(request.url).searchParams.get('url');
    if (!target) {
      return new Response('Paramètre ?url= manquant', { status: 400, headers: corsHeaders() });
    }

    // Sécurité : n'accepter que le domaine du drive
    if (ALLOWED_HOST) {
      try {
        if (new URL(target).hostname !== ALLOWED_HOST) {
          return new Response('Domaine non autorisé', { status: 403, headers: corsHeaders() });
        }
      } catch {
        return new Response('URL invalide', { status: 400, headers: corsHeaders() });
      }
    }

    let upstream;
    try {
      // redirect: 'follow' → le relais suit la redirection 303 de Nextcloud
      upstream = await fetch(target, { redirect: 'follow' });
    } catch (e) {
      return new Response('Erreur de récupération : ' + e, { status: 502, headers: corsHeaders() });
    }

    const headers = new Headers(upstream.headers);
    for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
    headers.delete('content-security-policy');
    headers.delete('content-security-policy-report-only');
    headers.delete('x-frame-options');

    return new Response(upstream.body, { status: upstream.status, headers });
  }
};

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Expose-Headers': '*'
  };
}
