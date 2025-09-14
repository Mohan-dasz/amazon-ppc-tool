# routers/keywords.py
import os
import re
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from core.config import settings

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

# ---------- Request/Response models ----------
class ScrapeRequest(BaseModel):
    keyword: str
    max_results: Optional[int] = 50
    min_volume: Optional[int] = 0
    marketplace: Optional[str] = "India"
    headless: Optional[bool] = True


class KeywordHit(BaseModel):
    keyword: str
    search_volume: Optional[int] = None
    extra: Optional[dict] = None


# ---------- Playwright Helium10 client ----------
_client_lock = asyncio.Lock()
_client_instance = None


class Helium10Client:
    def __init__(self, email: str, password: str, user_data_dir: str, headless: bool):
        self.email = email
        self.password = password
        self.user_data_dir = os.path.expanduser(user_data_dir)
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None
        self._init_lock = asyncio.Lock()

    async def initialize(self):
        async with self._init_lock:
            if self.context:
                return
            self.playwright = await async_playwright().start()
            # persistent context will save cookies & localStorage so session persists
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()

    async def close(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def _is_logged_in(self):
        try:
            if not self.page:
                return False
            # look for dashboard or sign out links
            if await self.page.locator("text=Dashboard").count() > 0:
                return True
            if await self.page.locator("text=Sign Out").count() > 0:
                return True
            if "members.helium10.com" in self.page.url and "/user/signin" not in self.page.url:
                return True
        except Exception:
            return False
        return False

    async def login_if_needed(self):
        if not self.email or not self.password:
            raise RuntimeError("HELIUM10_EMAIL and HELIUM10_PASSWORD must be set in environment (or settings).")

        await self.initialize()
        if await self._is_logged_in():
            logger.debug("Helium10: found existing logged-in session.")
            return

        signin_url = "https://members.helium10.com/user/signin"
        await self.page.goto(signin_url, timeout=60000)
        await self.page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)

        # Try to fill fields robustly
        try:
            # label-based selectors preferred
            if await self.page.get_by_label("Email").count() > 0:
                await self.page.get_by_label("Email").fill(self.email)
            elif await self.page.locator("input[type='email']").count() > 0:
                await self.page.fill("input[type='email']", self.email)
            else:
                # fallback to first input
                inputs = self.page.locator("input")
                if await inputs.count() >= 1:
                    await inputs.nth(0).fill(self.email)

            if await self.page.get_by_label("Password").count() > 0:
                await self.page.get_by_label("Password").fill(self.password)
            elif await self.page.locator("input[type='password']").count() > 0:
                await self.page.fill("input[type='password']", self.password)
            else:
                inputs = self.page.locator("input")
                if await inputs.count() >= 2:
                    await inputs.nth(1).fill(self.password)

            # Click sign-in
            if await self.page.locator("button:has-text('Log In')").count():
                await self.page.click("button:has-text('Log In')")
            elif await self.page.locator("button:has-text('Sign In')").count():
                await self.page.click("button:has-text('Sign In')")
            elif await self.page.locator("button[type='submit']").count():
                await self.page.click("button[type='submit']")
            else:
                await self.page.keyboard.press("Enter")

            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            if not await self._is_logged_in():
                await asyncio.sleep(3)
                if not await self._is_logged_in():
                    raise RuntimeError("Helium10 login failed. Check credentials or site flow.")
        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"Timeout during Helium10 login: {e}") from e

    async def set_marketplace(self, marketplace_name: str = "India"):
        # best-effort; UI may differ. Return True if appears to have set.
        try:
            # several heuristics to find marketplace selector
            if await self.page.locator("button:has-text('Marketplace')").count():
                await self.page.click("button:has-text('Marketplace')")
                await asyncio.sleep(0.5)
                if await self.page.locator(f"text={marketplace_name}").count():
                    await self.page.click(f"text={marketplace_name}")
                    await asyncio.sleep(1)
                    return True

            if await self.page.locator("select#marketplace, select[name='marketplace']").count():
                await self.page.select_option("select#marketplace, select[name='marketplace']", label=marketplace_name)
                await asyncio.sleep(1)
                return True
        except Exception as e:
            logger.debug("Marketplace switch attempt failed: %s", e)
        return False

    async def scrape_magnet(self, seed_keyword: str, max_results: int = 50, min_volume: int = 0, marketplace: str = "India") -> List[dict]:
        await self.login_if_needed()

        try:
            await self.page.goto("https://www.helium10.com/tools/keyword-research/magnet/", timeout=60000)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            await self.set_marketplace(marketplace)
        except Exception as e:
            logger.debug("Failed to open Magnet page: %s", e)

        # Try to fill seed field (multiple fallbacks)
        seed_selectors = [
            "input[placeholder*='seed']",
            "input[placeholder*='keyword']",
            "input[type='search']",
            "input[name='keyword']",
            "input[aria-label*='keyword']",
            "input"
        ]

        filled = False
        for sel in seed_selectors:
            try:
                if await self.page.locator(sel).count() > 0:
                    await self.page.fill(sel, seed_keyword)
                    filled = True
                    break
            except Exception:
                continue

        if not filled:
            # fallback JS set
            await self.page.evaluate("(k) => { const i = document.querySelector('input'); if(i){ i.focus(); i.value = k; i.dispatchEvent(new Event('input',{bubbles:true})); } }", seed_keyword)

        # submit (try button text or Enter)
        try:
            if await self.page.locator("button:has-text('Search')").count():
                await self.page.click("button:has-text('Search')")
            elif await self.page.locator("button:has-text('Find Keywords')").count():
                await self.page.click("button:has-text('Find Keywords')")
            else:
                await self.page.keyboard.press("Enter")
        except Exception:
            pass

        await asyncio.sleep(1.2)

        result_wait_selectors = [
            "table tbody tr",
            ".magnet-table tbody tr",
            ".results-table tbody tr",
            ".keyword-results tr",
            ".results-list .result"
        ]

        results = []
        for sel in result_wait_selectors:
            try:
                if await self.page.locator(sel).count() > 0:
                    rows = await self.page.locator(sel).all()
                    for i, row in enumerate(rows):
                        if i >= max_results:
                            break
                        try:
                            tds = []
                            try:
                                tds = await row.locator("td").all_inner_texts()
                            except Exception:
                                tds = [l.strip() for l in (await row.inner_text()).splitlines() if l.strip()]

                            if not tds:
                                continue

                            candidate_keyword = tds[0].strip()
                            candidate_volume = None
                            if len(tds) >= 2:
                                candidate_volume = _parse_int_from_string(tds[1])
                            else:
                                candidate_volume = _parse_int_from_string(" ".join(tds))

                            if candidate_volume is None:
                                candidate_volume = 0

                            if candidate_volume >= min_volume:
                                results.append({"keyword": candidate_keyword, "search_volume": candidate_volume, "raw_cells": tds})
                        except Exception as e:
                            logger.debug("row parse error: %s", e)
                            continue
                    break
            except Exception:
                continue

        # fallback scanning
        if not results:
            kw_elements = self.page.locator(".keyword")
            vol_elements = self.page.locator(".volume")
            if await kw_elements.count() > 0:
                count = min(await kw_elements.count(), max_results)
                for idx in range(count):
                    kw = (await kw_elements.nth(idx).inner_text()).strip()
                    vol = None
                    if await vol_elements.count() > idx:
                        vol = _parse_int_from_string(await vol_elements.nth(idx).inner_text())
                    results.append({"keyword": kw, "search_volume": vol or 0, "raw_cells": []})

        # dedupe and sort
        dedup = {}
        filtered = []
        for r in results:
            k = r["keyword"].lower()
            if k in dedup:
                continue
            dedup[k] = True
            if r.get("search_volume", 0) >= min_volume or min_volume == 0:
                filtered.append(r)

        filtered_sorted = sorted(filtered, key=lambda x: x.get("search_volume") or 0, reverse=True)
        return filtered_sorted[:max_results]


def _parse_int_from_string(s: str) -> Optional[int]:
    if not s or not isinstance(s, str):
        return None
    cleaned = re.sub(r"[^\d]", "", s)
    try:
        return int(cleaned) if cleaned else None
    except Exception:
        return None


async def get_client_once():
    global _client_instance
    async with _client_lock:
        if _client_instance is None:
            client = Helium10Client(
                email=settings.HELIUM10_EMAIL,
                password=settings.HELIUM10_PASSWORD,
                user_data_dir=settings.HELIUM10_USER_DATA_DIR,
                headless=settings.HELIUM10_HEADLESS
            )
            await client.initialize()
            _client_instance = client
        return _client_instance


@router.post("/keywords/scrape", response_model=List[KeywordHit])
async def scrape_keywords(req: ScrapeRequest):
    if not req.keyword or len(req.keyword.strip()) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="keyword is required")

    try:
        client = await get_client_once()
    except Exception as e:
        logger.error("Failed to init Helium10 client: %s", e)
        raise HTTPException(status_code=500, detail=f"Playwright init error: {e}")

    # headful debug option
    if req.headless is False and client.headless:
        await client.close()
        new_client = Helium10Client(
            email=client.email,
            password=client.password,
            user_data_dir=client.user_data_dir,
            headless=False
        )
        await new_client.initialize()
        async with _client_lock:
            global _client_instance
            _client_instance = new_client
        client = new_client

    try:
        raw = await client.scrape_magnet(seed_keyword=req.keyword, max_results=req.max_results, min_volume=req.min_volume, marketplace=req.marketplace)
        out = []
        for r in raw:
            out.append(KeywordHit(keyword=r.get("keyword"), search_volume=r.get("search_volume"), extra={"raw": r.get("raw_cells", [])}))
        return out
    except Exception as e:
        logger.exception("Scrape failed")
        raise HTTPException(status_code=500, detail=str(e))
