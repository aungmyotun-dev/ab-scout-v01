import msgpack

from core.browser import BrowserManager


def log_response(response):

    if "application/x-msgpack" not in response.headers.get(
        "content-type", ""
    ):
        return

    if "/api/poll/" not in response.url:
        return

    print("=" * 80)
    print(response.url)

    try:
        data = msgpack.unpackb(
            response.body(),
            raw=False,
        )

        print(type(data))

        if isinstance(data, dict):
            print(data.keys())

        elif isinstance(data, list):
            print("LEN =", len(data))

    except Exception as e:
        print(e)


browser = BrowserManager()

try:

    browser.start()

    browser.page.on(
        "response",
        log_response,
    )

    browser.open(
    "https://beta.asianbookie.net/en/matches/odds/FBB4BCEF9BE0EDE03520A0E4C1E117A9/friendlies/31-07-2026/mallorca-vs-al-ittihad"
    )

    print("Browser opened.")
    input("Press ENTER after clicking AH / Odds / History tab...")

    browser.page.wait_for_timeout(12000)

finally:

    browser.stop()
