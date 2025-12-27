"""Automate Grok favorites downloads and reruns via Playwright."""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


FAVORITES_URL = "https://grok.com/imagine/favorites"


@dataclass(frozen=True)
class GrokSelectors:
    checkbox_selector: str
    item_container_selector: str
    download_button_selector: str
    hd_toggle_selector: str
    prompt_selector: str
    prompt_input_selector: str
    rerun_button_selector: str
    open_item_selector: Optional[str] = None


DEFAULT_SELECTORS = GrokSelectors(
    checkbox_selector="input[type=\"checkbox\"]",
    item_container_selector="article, div",
    download_button_selector=(
        "button:has-text(\"Download\"), a:has-text(\"Download\")"
    ),
    hd_toggle_selector="button:has-text(\"HD\"), button:has-text(\"Upscale\")",
    prompt_selector=(
        "[data-testid*=\"prompt\"], [data-prompt], .prompt, textarea"
    ),
    prompt_input_selector="textarea",
    rerun_button_selector=(
        "button:has-text(\"Regenerate\"), button:has-text(\"Generate\")"
    ),
    open_item_selector=None,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Grok favorites downloader with HD upscale + rerun",
    )
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path("grok_profile"),
        help="Persistent browser profile directory.",
    )
    parser.add_argument(
        "--download-dir",
        type=Path,
        default=Path("downloads"),
        help="Directory to store downloaded videos.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional JSON file to override selectors.",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=0,
        help="Limit number of checked items to process (0 = no limit).",
    )
    parser.add_argument(
        "--wait-login",
        action="store_true",
        help="Wait for manual login before continuing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report matched items without downloading.",
    )
    return parser


def load_selectors(config_path: Optional[Path]) -> GrokSelectors:
    if not config_path:
        return DEFAULT_SELECTORS
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return GrokSelectors(**{**DEFAULT_SELECTORS.__dict__, **data})


def prompt_for_login(wait_login: bool) -> None:
    if not wait_login:
        return
    print("브라우저에서 Grok에 로그인한 뒤 Enter를 눌러 진행하세요.")
    input()


def wait_for_download(page, download_dir: Path, timeout_ms: int = 120_000) -> Path:
    with page.expect_download(timeout=timeout_ms) as download_info:
        pass
    download = download_info.value
    suggested = download.suggested_filename
    target = download_dir / suggested
    download.save_as(target)
    return target


def extract_prompt_text(item_handle, selectors: GrokSelectors) -> Optional[str]:
    for selector in selectors.prompt_selector.split(","):
        selector = selector.strip()
        if not selector:
            continue
        handle = item_handle.query_selector(selector)
        if handle:
            prompt_value = handle.get_attribute("data-prompt")
            if prompt_value:
                return prompt_value.strip()
            if handle.evaluate("el => 'value' in el"):
                value = handle.get_attribute("value") or ""
                if value.strip():
                    return value.strip()
            text = handle.inner_text().strip()
            if text:
                return text
    return None


def run_rerun(page, selectors: GrokSelectors, prompt_text: str) -> None:
    input_box = page.locator(selectors.prompt_input_selector).first
    input_box.fill(prompt_text)
    rerun_button = page.locator(selectors.rerun_button_selector).first
    rerun_button.click()


def handle_item(page, item_handle, selectors: GrokSelectors, download_dir: Path) -> None:
    if selectors.open_item_selector:
        opener = item_handle.query_selector(selectors.open_item_selector)
        if opener:
            opener.click()
            time.sleep(1)

    hd_toggle = item_handle.query_selector(selectors.hd_toggle_selector)
    if hd_toggle:
        hd_toggle.click()

    download_button = item_handle.query_selector(selectors.download_button_selector)
    if not download_button:
        download_button = page.query_selector(selectors.download_button_selector)

    if download_button:
        download_button.click()
        downloaded_path = wait_for_download(page, download_dir)
        print(f"다운로드 완료: {downloaded_path}")
    else:
        print("다운로드 버튼을 찾지 못했습니다.")

    prompt_text = extract_prompt_text(item_handle, selectors)
    if not prompt_text:
        prompt_text = extract_prompt_text(page, selectors)

    if prompt_text:
        run_rerun(page, selectors, prompt_text)
        print("프롬프트 재실행 완료")
    else:
        print("프롬프트를 찾지 못했습니다.")


def run_automation(
    profile_dir: Path,
    download_dir: Path,
    selectors: GrokSelectors,
    *,
    headless: bool,
    wait_login: bool,
    max_items: int,
    dry_run: bool,
) -> int:
    profile_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            accept_downloads=True,
        )
        page = context.new_page()
        page.goto(FAVORITES_URL, wait_until="domcontentloaded")
        prompt_for_login(wait_login)

        try:
            page.wait_for_url("**/imagine/favorites", timeout=30_000)
        except PlaywrightTimeoutError:
            print("favorites 페이지에 도달하지 못했습니다. 로그인 상태를 확인하세요.")

        checkboxes = page.query_selector_all(selectors.checkbox_selector)
        checked_items = []
        for checkbox in checkboxes:
            if checkbox.is_checked():
                container = checkbox.evaluate_handle(
                    "(el, selector) => el.closest(selector)",
                    selectors.item_container_selector,
                )
                checked_items.append(container)

        if max_items > 0:
            checked_items = checked_items[:max_items]

        print(f"선택된 항목 수: {len(checked_items)}")
        if dry_run:
            context.close()
            return 0

        for item in checked_items:
            handle_item(page, item, selectors, download_dir)

        context.close()

    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    selectors = load_selectors(args.config)

    return run_automation(
        args.profile_dir,
        args.download_dir,
        selectors,
        headless=args.headless,
        wait_login=args.wait_login,
        max_items=args.max_items,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
