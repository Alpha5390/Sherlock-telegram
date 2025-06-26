import asyncio
import aiohttp
import json
from datetime import datetime
from bs4 import BeautifulSoup
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console

console = Console()

SITES = [
    {"name": "GitHub", "url": "https://github.com/{}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}"},
    {"name": "Telegram", "url": "https://t.me/{}"},
    {"name": "DeviantArt", "url": "https://www.deviantart.com/{}"},
    {"name": "Quora", "url": "https://www.quora.com/profile/{}"},
    {"name": "Instagram", "url": "https://www.instagram.com/{}/"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}"},
    {"name": "Facebook", "url": "https://www.facebook.com/{}"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{}"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}"},
    {"name": "Discord", "url": "https://discord.com/users/{}"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}"},
{"name": "Tumblr", "url": "https://{}.tumblr.com"},
{"name": "Medium", "url": "https://medium.com/@{}"},
{"name": "Snapchat", "url": "https://www.snapchat.com/add/{}"},
{"name": "Vimeo", "url": "https://vimeo.com/{}"},
{"name": "SoundCloud", "url": "https://soundcloud.com/{}"},
{"name": "Behance", "url": "https://www.behance.net/{}"},
{"name": "Flickr", "url": "https://www.flickr.com/people/{}"},
{"name": "Goodreads", "url": "https://www.goodreads.com/user/show/{}"},
{"name": "Mixcloud", "url": "https://www.mixcloud.com/{}"},
{"name": "Dribbble", "url": "https://dribbble.com/{}"},
{"name": "ProductHunt", "url": "https://www.producthunt.com/@{}"},
{"name": "Kaggle", "url": "https://www.kaggle.com/{}"},
{"name": "AboutMe", "url": "https://about.me/{}"},
{"name": "AngelList", "url": "https://angel.co/u/{}"},
{"name": "Keybase", "url": "https://keybase.io/{}"},
{"name": "500px", "url": "https://500px.com/p/{}"},
{"name": "Tripadvisor", "url": "https://www.tripadvisor.com/Profile/{}"},
{"name": "Bandcamp", "url": "https://{}.bandcamp.com"},
{"name": "Blogger", "url": "https://{}.blogspot.com"},
{"name": "Weebly", "url": "https://{}.weebly.com"},
{"name": "Replit", "url": "https://replit.com/@{}"},
{"name": "Gravatar", "url": "https://en.gravatar.com/{}"},
{"name": "Codecademy", "url": "https://www.codecademy.com/profiles/{}"},
{"name": "Fiverr", "url": "https://www.fiverr.com/{}"},
{"name": "Freelancer", "url": "https://www.freelancer.com/u/{}"},
{"name": "Upwork", "url": "https://www.upwork.com/freelancers/~{}"},
{"name": "DevTo", "url": "https://dev.to/{}"},
{"name": "Hackerrank", "url": "https://www.hackerrank.com/{}"},
{"name": "Codepen", "url": "https://codepen.io/{}"},
{"name": "JSFiddle", "url": "https://jsfiddle.net/user/{}/"},
{"name": "Codewars", "url": "https://www.codewars.com/users/{}"},
{"name": "Leetcode", "url": "https://leetcode.com/{}"},
{"name": "Scribd", "url": "https://www.scribd.com/{}"},
{"name": "Etsy", "url": "https://www.etsy.com/shop/{}"},
{"name": "Wattpad", "url": "https://www.wattpad.com/user/{}"},
{"name": "Wikia", "url": "https://community.fandom.com/wiki/User:{}"},
{"name": "Gumroad", "url": "https://{}.gumroad.com"},
{"name": "Patreon", "url": "https://www.patreon.com/{}"},
{"name": "OnlyFans", "url": "https://onlyfans.com/{}"},
{"name": "Letterboxd", "url": "https://letterboxd.com/{}"},
{"name": "IFTTT", "url": "https://ifttt.com/p/{}"},
{"name": "BuyMeACoffee", "url": "https://www.buymeacoffee.com/{}"},
{"name": "ScoopIt", "url": "https://www.scoop.it/u/{}"},
{"name": "Wix", "url": "https://{}.wixsite.com"},
{"name": "GitLab", "url": "https://gitlab.com/{}"},
{"name": "Bitbucket", "url": "https://bitbucket.org/{}"},
{"name": "OpenStreetMap", "url": "https://www.openstreetmap.org/user/{}"},
{"name": "ArchiveOrg", "url": "https://archive.org/details/@{}"},
{"name": "CashApp", "url": "https://cash.app/{}"}
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def ai_check_username_exists(html, username):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ', strip=True).lower()
    username = username.lower()

    negative_keywords = [
        "not found", "404", "doesn't exist", "does not exist", "page not found",
        "sorry", "unavailable", "couldn’t find", "this page isn't available"
    ]

    for word in negative_keywords:
        if word in text:
            return False

    if username in text:
        return True

    return False

async def check_site(session, username, site_data, progress):
    url = site_data["url"].format(username)
    headers = {"User-Agent": USER_AGENT}
    try:
        async with session.get(url, headers=headers, timeout=15, ) as response:
            content = await response.text()
            exists = ai_check_username_exists(content, username)
            progress.update(progress.tasks[0].id, advance=1)
            return {
                "site": site_data["name"],
                "url": url,
                "exists": exists,
                "status": response.status,
                "error": None
            }
    except Exception as e:
        progress.update(progress.tasks[0].id, advance=1)
        return {
            "site": site_data["name"],
            "url": url,
            "exists": False,
            "status": None,
            "error": str(e)
        }

async def check_username(username):
    console.print(f"\nFoydalanuvchi nomi: {username}")
    console.print(f"Platformalar: {len(SITES)} ta\n")

    results = []
    async with aiohttp.ClientSession() as session:
        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Tekshirilmoqda...", total=len(SITES))
            tasks = [check_site(session, username, site, progress) for site in SITES]
            for future in asyncio.as_completed(tasks):
                results.append(await future)

    found = [r for r in results if r["exists"]]
    not_found = [r for r in results if not r["exists"] and r["error"] is None]
    errors = [r for r in results if r["error"]]

    if found:
        console.print("\nQuydagi saytlarda topildi:")
        for r in found:
            console.print(f"  • {r['site']:>12} : {r['url']}")

    if not_found:
        console.print("\nQuydagi saytlarda topilmadi:")
        for r in not_found:
            console.print(f"  • {r['site']:>12} : {r['url']}")

    if errors:
        console.print("\nXatoliklar:")
        for r in errors:
            console.print(f"  • {r['site']:>12} : {r['error']}")

    return results, found, not_found, errors



def main():
    console.rule("FOYDALANUVCHI NOMI TEKSHIRUV DASTURI")
    username = console.input("\nFoydalanuvchi nomini kiriting: ").strip()
    if not username:
        console.print("Foydalanuvchi nomi kiritilmadi.")
        return

    loop = asyncio.get_event_loop()
    results, found, not_found, errors = loop.run_until_complete(check_username(username))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nDastur to‘xtatildi.")
    except Exception as e:
        console.print(f"\nXato yuz berdi: {e}")
