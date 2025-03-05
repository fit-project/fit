import subprocess
import re
from configparser import ConfigParser


def get_version_from_latest_git_tag():
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"]
        ).strip()
        return tag.decode("utf-8")
    except subprocess.CalledProcessError:
        return None


def get_version_from_pyproject():
    try:
        with open("pyproject.toml", "r") as file:
            for line in file:
                match = re.match(r'^\s*version\s*=\s*"(.*?)"\s*$', line)
                if match:
                    return match.group(1)
        return None
    except FileNotFoundError:
        return None


def get_version():
    version = get_version_from_latest_git_tag()
    if version is None:
        version = get_version_from_pyproject()
    return version


def update_version_in_pyproject_toml():
    stripped_version = VERSION[1:] if VERSION.startswith("v") else VERSION

    with open("pyproject.toml", "r") as file:
        content = file.read()

    new_content = re.sub(
        r'version\s*=\s*"[0-9a-zA-Z.-]+"', f'version = "{stripped_version}"', content
    )

    with open("pyproject.toml", "w") as file:
        file.write(new_content)


def update_version_in_config_ini():
    config = ConfigParser()
    config.read("assets/config.ini")

    if config.has_section("fit_properties"):
        config.set("fit_properties", "tag_name", VERSION)

    with open("assets/config.ini", "w") as configfile:
        config.write(configfile)


def update_version():
    update_version_in_pyproject_toml()
    update_version_in_config_ini()


VERSION = get_version()

if VERSION is not None:
    update_version()
