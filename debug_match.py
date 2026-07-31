import msgpack
from collections import Counter

from core.browser import BrowserManager


def log_response(response):

    if "/api/poll/match?" not in response.url:
        return

    body = response.body()

    data = msgpack.unpackb(
        body,
        raw=False,
    )

    print("=" * 80)
    print("MATCH API")
    print("=" * 80)
    print("URL :", response.url)
    print("ROWS:", len(data))

    # --------------------------------------------------
    # Row Length Statistics
    # --------------------------------------------------

    counter = Counter()

    for row in data:

        if isinstance(row, list):
            counter[len(row)] += 1

    print("\nRow Length Counter")
    print("=" * 80)

    for length, count in sorted(counter.items()):
        print(f"{length:>3} columns : {count} rows")

    # --------------------------------------------------
    # Sample Row for EACH schema
    # --------------------------------------------------

    printed = set()

    for row in data:

        if not isinstance(row, list):
            continue

        l = len(row)

        if l in printed:
            continue

        printed.add(l)

        print("\n" + "=" * 80)
        print(f"SAMPLE ROW ({l} columns)")
        print("=" * 80)

        for i, value in enumerate(row):
            print(f"{i:02d} : {value}")

    print("\nFinished.")
    exit()


browser = BrowserManager()

try:

    browser.start()

    browser.page.on(
        "response",
        log_response,
    )

    browser.open(
        "https://beta.asianbookie.net/en/upcoming"
    )

    browser.page.wait_for_timeout(15000)

finally:

    browser.stop()