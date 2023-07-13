import platform as platform_
from os import environ
from typing import Dict, List


def parse_command(commands: List[str]) -> str:
    return "-".join(commands).lower()


def parse_language(language: str, config: Dict) -> List[str]:
    """Return language list for page matching.

    If language is specified or configured, use it as only choice.
    Otherwise make the list based on env `LANG` and `LANGUAGE`.
    # pylint: disable=line-too-long
    For detailed logic, see https://github.com/tldr-pages/tldr/blob/main/CLIENT-SPECIFICATION.md#language
    """  # noqa: E501
    language = language or config.get("language", "")
    if language:
        return [language.lower()]

    def extractor(x: str) -> str:
        return x.split("_", maxsplit=1)[0].lower()

    lang = extractor(environ.get("LANG", ""))
    if not lang:
        return ["en"]
    languages = [
        extractor(item) for item in environ.get("LANGUAGE", "").split(":") if item
    ]
    if lang not in languages:
        languages.append(lang)
    if "en" not in languages:
        languages.append("en")
    return [language.lower() for language in languages]


def parse_platform(platform: str) -> str:
    return platform.lower() or guess_os()


def guess_os():
    system_to_platform = {
        "Linux": "linux",
        "Darwin": "osx",
        "Java": "sunos",
        "Windows": "windows",
        "Android": "android",
    }
    return system_to_platform.get(platform_.system(), "linux")
