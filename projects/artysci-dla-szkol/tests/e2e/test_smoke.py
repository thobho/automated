from axe_playwright_python.sync_playwright import Axe


def test_home(page, base_url, shot):
    response = page.goto(base_url + "/")
    assert response.status == 200
    assert page.locator("h1").inner_text().strip() != ""
    shot("home-desktop")


def test_healthz(page, base_url):
    response = page.goto(base_url + "/healthz")
    assert response.status == 200
    assert response.json() == {"db": "ok"}


def test_home_mobile_375(browser, base_url, shot_dir):
    context = browser.new_context(viewport={"width": 375, "height": 800})
    page = context.new_page()
    page.goto(base_url + "/")
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    assert scroll_width <= 375, f"horizontal overflow at 375 px: {scroll_width}"
    page.screenshot(path=str(shot_dir / "home-375.png"), full_page=True)
    context.close()


def test_axe_no_critical_violations(page, base_url):
    page.goto(base_url + "/")
    results = Axe().run(page)
    critical = [v for v in results.response["violations"] if v["impact"] == "critical"]
    assert not critical, [f"{v['id']}: {v['help']}" for v in critical]
