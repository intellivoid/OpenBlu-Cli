from setuptools import setup, find_packages
import platform
import subprocess


with open("README.md", "r") as fh:
    long_description = fh.read()



setup(
    name="OpenBlu-cli",
    version="0.1",
    author="Intellivoid Technologies",
    author_email="nocturn9x@intellivoid.info",
    description="Official OpenBlu command-line interface to fetch and list available servers, filter them and connect to them with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intellivoid/OpenBlu-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache License 2.0"
    ],
    python_requires='>=3.6',
)

if platform.system() == 'Windows':
    print("Windows System detetcted: There is no way to install the OpenVPN client automatically, please refer to https://openvpn.net/vpn-server-resources/installation-guide-for-openvpn-connect-client-on-windows/#Downloading_and_installing_the_OpenVPN_Connect_Client_for_Windows")

elif platform.system() == 'Linux':
    try:
        prompted = input("Linux System Detected\nWould you like to install the OpenVPN client? (Y/N) [N]: ")
    except (EOFError, KeyboardInterrupt):
        exit()
    if prompted.lower() in ("y", "yes"):
        print("Spawning a subprocess...")
        command = subprocess.run(["apt-get", "install", "openvpn"])
        if command.returncode != 0:
            print("Something went wrong and it was not possible to install the OpenVPN client automatically, please refer to https://openvpn.net/vpn-server-resources/connecting-to-access-server-with-linux/#OpenVPN_open_source_OpenVPN_CLI_program")
        print(f"Done! The command exited with exit code {command.returncode}")
