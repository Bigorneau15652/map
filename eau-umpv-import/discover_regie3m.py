#!/usr/bin/env python3
"""Reconnaissance script for https://ael.regiedeseaux3m.fr/ (Regie des Eaux
de Montpellier Mediterranee Metropole).

Unlike toutsurmoneau.fr (SUEZ), there is no known open-source client for
this portal, and it could not be inspected ahead of time (no network access
to arbitrary sites from the environment these scripts were written in). This
script is step one of an iterative build: it logs in with a real browser
(Playwright), navigates towards the consumption/history pages, and dumps
everything useful (which JSON API calls the page makes, screenshots, page
HTML) so the next iteration can replace the guesswork below with exact
selectors/endpoints.

It is deliberately defensive: every stage is wrapped so a failure in one
does not prevent capturing diagnostics from the stages that did work.

Required env vars:
  REGIE3M_USERNAME   Login for ael.regiedeseaux3m.fr
  REGIE3M_PASSWORD   Password for ael.regiedeseaux3m.fr

Output (written to ./discover-output/):
  api-calls.json      Every XHR/fetch response with a JSON content-type
                       seen during the whole session (url, status, body).
  before-login.png, after-login.png, after-nav.png   Screenshots.
  page-after-login.html   Full HTML of the page right after login.
  log.txt              Narration of what was attempted and what happened.
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = "https://ael.regiedeseaux3m.fr/"
OUT_DIR = Path("discover-output")

LOGIN_TEXT_RE = re.compile(r"identifiant|utilisateur|e-?mail|login|username", re.I)
PASSWORD_TEXT_RE = re.compile(r"mot de passe|password", re.I)
SUBMIT_TEXT_RE = re.compile(r"connexion|connecter|valider|se connecter|login", re.I)
CONSUMPTION_TEXT_RE = re.compile(r"consommation|conso|historique|compteur", re.I)


class Narrator:
    def __init__(self, path: Path):
        self.lines = []
        self.path = path

    def log(self, msg: str) -> None:
        print(msg)
        self.lines.append(msg)

    def save(self) -> None:
        self.path.write_text("\n".join(self.lines), encoding="utf-8")


async def find_login_fields(page):
    """Best-effort search for username/password inputs, several strategies."""
    username_input = None
    password_input = None

    # Strategy 1: obvious input types.
    try:
        candidates = await page.locator("input[type=email], input[type=text]").all()
        if candidates:
            username_input = candidates[0]
    except Exception:
        pass
    try:
        pw = page.locator("input[type=password]").first
        if await pw.count():
            password_input = pw
    except Exception:
        pass

    # Strategy 2: label/placeholder text.
    if username_input is None:
        for loc_fn in (page.get_by_label, page.get_by_placeholder):
            try:
                loc = loc_fn(LOGIN_TEXT_RE)
                if await loc.count():
                    username_input = loc.first
                    break
            except Exception:
                continue
    if password_input is None:
        for loc_fn in (page.get_by_label, page.get_by_placeholder):
            try:
                loc = loc_fn(PASSWORD_TEXT_RE)
                if await loc.count():
                    password_input = loc.first
                    break
            except Exception:
                continue

    return username_input, password_input


async def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    narrator = Narrator(OUT_DIR / "log.txt")

    username = os.environ.get("REGIE3M_USERNAME")
    password = os.environ.get("REGIE3M_PASSWORD")
    if not username or not password:
        narrator.log("Missing REGIE3M_USERNAME / REGIE3M_PASSWORD.")
        narrator.save()
        sys.exit(1)

    api_calls = []

    async def on_response(response):
        try:
            headers = await response.all_headers()
            content_type = headers.get("content-type", "")
            if "json" not in content_type:
                return
            try:
                body = await response.text()
            except Exception:
                body = "<unreadable body>"
            api_calls.append({
                "method": response.request.method,
                "url": response.url,
                "status": response.status,
                "body_excerpt": body[:2000],
            })
        except Exception as e:
            narrator.log(f"  (failed to record response {response.url}: {e!r})")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        page.on("response", lambda r: asyncio.create_task(on_response(r)))

        narrator.log(f"Navigating to {BASE_URL}")
        try:
            await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            narrator.log(f"goto() failed or timed out (continuing anyway): {e!r}")

        try:
            await page.screenshot(path=str(OUT_DIR / "before-login.png"), full_page=True)
        except Exception as e:
            narrator.log(f"screenshot before login failed: {e!r}")

        narrator.log(f"Page title after initial load: {await page.title()!r}, url={page.url!r}")

        username_input, password_input = await find_login_fields(page)
        narrator.log(f"username_input found: {username_input is not None}; "
                      f"password_input found: {password_input is not None}")

        if username_input is not None and password_input is not None:
            try:
                await username_input.fill(username)
                await password_input.fill(password)
                narrator.log("Filled username/password fields.")
            except Exception as e:
                narrator.log(f"Failed to fill login fields: {e!r}")

            submitted = False
            try:
                submit_btn = page.get_by_role("button", name=SUBMIT_TEXT_RE)
                if await submit_btn.count():
                    await submit_btn.first.click()
                    submitted = True
                    narrator.log("Clicked a submit-like button.")
            except Exception as e:
                narrator.log(f"Could not click submit button: {e!r}")
            if not submitted:
                try:
                    await password_input.press("Enter")
                    submitted = True
                    narrator.log("Submitted login by pressing Enter in the password field.")
                except Exception as e:
                    narrator.log(f"Could not submit by pressing Enter: {e!r}")

            try:
                await page.wait_for_load_state("networkidle", timeout=20000)
            except Exception as e:
                narrator.log(f"wait_for_load_state after login timed out (continuing): {e!r}")
        else:
            narrator.log("Could not locate both login fields; skipping submit.")

        narrator.log(f"Page title after login attempt: {await page.title()!r}, url={page.url!r}")
        try:
            await page.screenshot(path=str(OUT_DIR / "after-login.png"), full_page=True)
        except Exception as e:
            narrator.log(f"screenshot after login failed: {e!r}")
        try:
            (OUT_DIR / "page-after-login.html").write_text(await page.content(), encoding="utf-8")
        except Exception as e:
            narrator.log(f"dumping HTML after login failed: {e!r}")

        try:
            nav_link = page.get_by_text(CONSUMPTION_TEXT_RE)
            if await nav_link.count():
                narrator.log(f"Found {await nav_link.count()} element(s) matching a consumption-like label, clicking the first.")
                await nav_link.first.click()
                await page.wait_for_load_state("networkidle", timeout=20000)
            else:
                narrator.log("No consumption/history-like nav link found by text.")
        except Exception as e:
            narrator.log(f"Navigating to consumption page failed: {e!r}")

        narrator.log(f"Final page title: {await page.title()!r}, url={page.url!r}")
        try:
            await page.screenshot(path=str(OUT_DIR / "after-nav.png"), full_page=True)
        except Exception as e:
            narrator.log(f"final screenshot failed: {e!r}")

        await browser.close()

    (OUT_DIR / "api-calls.json").write_text(json.dumps(api_calls, indent=2), encoding="utf-8")
    narrator.log(f"Captured {len(api_calls)} JSON API response(s), see api-calls.json")
    narrator.save()


if __name__ == "__main__":
    asyncio.run(main())
