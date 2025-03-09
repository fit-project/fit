#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from importlib import util
import distutils.spawn
from distutils.version import StrictVersion
import os
import sys
import hashlib
import ntplib
import re
import subprocess
import tempfile

import urllib.request
from urllib.parse import urlparse


from datetime import datetime, timezone
from configparser import SafeConfigParser, ConfigParser

from whois import NICClient, extract_domain, IPV4_OR_V6
import socket

import requests
import urllib3

urllib3.disable_warnings()

from controller.configurations.tabs.language.language import (
    Language as LanguageController,
)


import ssl
import logging

logging.getLogger("scapy").setLevel(logging.CRITICAL)
import scapy.all as scapy

from contextlib import redirect_stdout

from nslookup import Nslookup


def get_platform():
    platforms = {
        "linux": "lin",
        "linux1": "lin",
        "linux2": "lin",
        "darwin": "macos",
        "win32": "win",
    }

    if sys.platform not in platforms:
        return "other"

    return platforms[sys.platform]


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode.
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


def has_new_portable_version():
    parser = ConfigParser()
    parser.read(resolve_path("assets/config.ini"))
    url = parser.get("fit_properties", "fit_latest_version_url")

    with requests.get(url, stream=True, timeout=10, verify=False) as response:
        try:
            remote_tag_name = response.json()["tag_name"]
            local_tag_name = parser.get("fit_properties", "tag_name")

            remote_tag_name = re.findall(r"(?:(\d+\.(?:\d+\.)*\d+))", remote_tag_name)
            local_tag_name = re.findall(r"(?:(\d+\.(?:\d+\.)*\d+))", local_tag_name)

            if (
                len(remote_tag_name) == 1
                and len(local_tag_name) == 1
                and StrictVersion(remote_tag_name[0]) > StrictVersion(local_tag_name[0])
            ):
                return True
            return False
        except Exception as e:
            raise Exception(e)


def calculate_hash(filename, algorithm):
    with open(filename, "rb") as f:
        file_hash = hashlib.new(algorithm)
        while chunk := f.read(8192):
            file_hash.update(chunk)

        return file_hash.hexdigest()


def get_ntp_date_and_time(server):
    try:
        ntpDate = None
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
    except Exception as exception:
        return exception

    return datetime.fromtimestamp(response.tx_time, timezone.utc)


def whois(url, flags=0):
    ip_match = IPV4_OR_V6.match(url)
    if ip_match:
        domain = url
        try:
            result = socket.gethostbyaddr(url)
        except socket.herror as e:
            return e.strerror
        else:
            domain = extract_domain(result[0])
    else:
        domain = extract_domain(url)

    # try builtin client
    nic_client = NICClient()

    return nic_client.whois_lookup(None, domain.encode("idna"), flags)


def nslookup(url, dns_server, enable_verbose_mode, enable_tcp):
    url = urlparse(url)
    netloc = url.netloc

    if not netloc:
        return "Don't find Network location part in the URL"
    else:
        netloc = netloc.split(":")[0]
        dns_query = Nslookup(
            dns_servers=[dns_server], verbose=enable_verbose_mode, tcp=enable_tcp
        )
        ips_record = dns_query.dns_lookup(netloc)

        return "\n".join(map(str, ips_record.response_full))


def traceroute(url, filename):
    url = urlparse(url)
    netloc = url.netloc

    if not netloc:
        print("Don't find Network location part in the URL")
    else:
        netloc = netloc.split(":")[0]

        with open(filename, "w") as f:
            with redirect_stdout(f):
                ans, unans = scapy.sr(
                    scapy.IP(dst=netloc, ttl=(1, 22), id=scapy.RandShort())
                    / scapy.TCP(flags=0x2),
                    timeout=10,
                )
                for snd, rcv in ans:
                    print(snd.ttl, rcv.src, isinstance(rcv.payload, scapy.TCP))


def get_headers_information(url):
    __url = urlparse(url)
    if not __url.netloc:
        return "Don't find Network location part in the URL"
    response = requests.get(url, verify=False)
    return response.headers


def check_if_peer_certificate_exist(url):
    __url = urlparse(url)
    if not __url.netloc:
        return False
    with requests.get(url, stream=True, timeout=10, verify=False) as response:
        try:
            response.raw.connection.sock.getpeercert()
            return True
        except Exception as e:
            return False


def get_peer_PEM_cert(url, port=443, timeout=10):
    url = urlparse(url)
    netloc = url.netloc

    if not netloc:
        return None
    else:
        if ":" in netloc:
            netloc, port = netloc.split(":")

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = socket.create_connection((netloc, port))
        sock = context.wrap_socket(conn, server_hostname=netloc)
        sock.settimeout(timeout)

        try:
            der_cert = sock.getpeercert(True)
        finally:
            sock.close()

        return ssl.DER_cert_to_PEM_cert(der_cert)


def save_PEM_cert_to_CER_cert(filename, certificate):
    try:
        with open(filename, "w+") as cer_file:
            if sys.version_info[0] >= 3:
                cer_file.write(certificate)
            else:
                cer_file.write(certificate)
    except IOError:
        print("Exception:  {0}".format(IOError.strerror))


def import_modules(start_path, start_module_name=""):
    py_files = []
    exclude = set(["test"])
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file.endswith(".py") and not file.endswith("__.py"):
                py_files.append(os.path.join(start_path, root, file))

    for py_file in py_files:
        module_name = (
            start_module_name + "." + os.path.split(py_file)[-1].rsplit(".", 1)[0]
        )
        spec = util.spec_from_file_location(module_name, py_file)
        module = util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)


def is_cmd(name):
    return distutils.spawn.find_executable(name) is not None


def get_version():
    parser = ConfigParser()
    parser.read(resolve_path("assets/config.ini"))
    version = parser.get("fit_properties", "tag_name")

    return version


def get_logo():
    logo_path = resolve_path(os.path.join("assets", "branding", "FIT-640.png"))

    return logo_path


def get_language():
    controller = LanguageController()
    return controller.options["language"]


# search for the first free port to bind the proxy
def find_free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    return sock.getsockname()[1]
