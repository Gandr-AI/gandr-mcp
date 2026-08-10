"""Self-check for the language parameter. Run it with: python test_languages.py"""

from gandr_mcp import server

SITE = [  # the 23 published on https://gandr.ai/languages/
    "Arabic", "Chinese", "Czech", "Danish", "Dutch", "English", "Finnish",
    "French", "German", "Greek", "Hindi", "Italian", "Japanese", "Korean",
    "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Spanish",
    "Swedish", "Turkish", "Ukrainian",
]


def main() -> None:
    assert sorted(server.LANGUAGES.values()) == sorted(SITE), "drifted from the site"

    sent: dict = {}

    def fake(path, body):
        sent["body"] = body
        return b"RIFFfake"

    server.KEY = "gnd_test"
    server._call = fake

    server.synthesize("hello")
    assert sent["body"]["language"] == "en", "default is no longer English"

    for code in server.LANGUAGES:
        assert not server.synthesize("x", language=code).startswith("error:"), code
        assert sent["body"]["language"] == code, code

    sent.clear()
    assert server.synthesize("x", language="xx").startswith("error: unsupported language")
    assert not sent, "a rejected language still reached the network"

    assert len(server.list_languages().splitlines()) == len(SITE)
    print(f"ok: {len(SITE)} languages, default en, bad codes rejected before the call")


if __name__ == "__main__":
    main()
