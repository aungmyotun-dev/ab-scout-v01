import msgpack

from core.browser import BrowserManager


def log_response(response):

    content_type = response.headers.get("content-type", "")

    if "application/x-msgpack" not in content_type:
        return

    # ---------------------------------------------------
    # Print every msgpack URL
    # ---------------------------------------------------

    print("=" * 80)
    print(response.url)

    # ---------------------------------------------------
    # MATCH API
    # ---------------------------------------------------

    if "/api/poll/match?" in response.url:

        body = response.body()

        data = msgpack.unpackb(
            body,
            raw=False,
        )

        print("=" * 80)
        print("MATCH API")
        print("=" * 80)

        print(type(data))

        if isinstance(data, dict):
            print("Keys :", data.keys())

        elif isinstance(data, list):
            print("Length :", len(data))
            print("First 5 rows:")
            for row in data[:5]:
                print(row)

        return

    # ---------------------------------------------------
    # UPCOMING API
    # ---------------------------------------------------

    if "/api/poll/upcoming" in response.url:

        body = response.body()

        data = msgpack.unpackb(
            body,
            raw=False,
        )

        print("=" * 80)
        print("UPCOMING API")
        print("=" * 80)

        print(type(data))

        if isinstance(data, list):
            print("Length :", len(data))

        elif isinstance(data, dict):
            print(data.keys())

        return


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

    browser.page.wait_for_timeout(10000)

finally:

    browser.stop()