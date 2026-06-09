import ctypes
import os
import sys
import urllib.error
import urllib.request
from enum import Enum

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Flowseal/zapret-discord-youtube/main/.service/version.txt"
GITHUB_RELEASE_URL = "https://github.com/Flowseal/zapret-discord-youtube/releases/tag/"
GITHUB_DOWNLOAD_URL = (
    "https://github.com/Flowseal/zapret-discord-youtube/releases/latest"
)

LOCAL_VERSION = os.environ.get("LOCAL_VERSION", "")


class DialogFlags(
    Enum
):  # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw
    I_WARN = 0x30  # MB_ICONWARNING
    I_INFO = 0x40  # MB_ICONINFORMATION
    # I_...
    R_OK = 0x0  # MB_OK
    R_OKCANCEL = 0x1  # MB_OKCANCEL
    # R_...


def open_release_page(version: str):
    os.startfile(GITHUB_RELEASE_URL + version)


def show_dialog(text: str, v_flag: DialogFlags, r_flag: DialogFlags = DialogFlags.R_OK):
    MessageBoxW = ctypes.windll.user32.MessageBoxW
    MessageBoxW.argtypes = (
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint,
    )
    MessageBoxW.restype = ctypes.c_int
    return MessageBoxW(
        None,
        text,
        "zapret",
        v_flag.value | r_flag.value,
    )


def fetch_latest(timeout=5):
    req = urllib.request.Request(
        GITHUB_VERSION_URL, headers={"Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8").strip()


def main():
    nonSoft = sys.argv[1] != "soft"

    try:
        github_version = fetch_latest()
    except (urllib.error.URLError, Exception) as e:
        show_dialog(
            f"Failed to fetch the latest version.\n{e.__class__.__name__}: {e}",
            DialogFlags.I_WARN,
        )
        return 1

    if not github_version:
        show_dialog("Failed to fetch the latest version.", DialogFlags.I_WARN)
        return 1

    if LOCAL_VERSION == github_version:
        if nonSoft:
            print(f"Latest version installed: {LOCAL_VERSION}")
        return 0

    text = f"Version {github_version} is available"

    if nonSoft:
        print(text)
        print("Release page: " + GITHUB_RELEASE_URL + github_version)
        open_release_page(github_version)
        input("Press Enter to continue...")
    elif (
        show_dialog(
            text + ", open the download page?",
            DialogFlags.I_INFO,
            DialogFlags.R_OKCANCEL,
        )
        == 1
    ):
        open_release_page(github_version)

    return 1


if __name__ == "__main__":
    code = main()
    print(f"ends with code {code}")
    sys.exit(code)
