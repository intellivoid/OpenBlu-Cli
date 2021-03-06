import argparse
import requests
import platform
from typing import Union
import json
from datetime import datetime
import os
from prettytable import PrettyTable
import subprocess


SYSTEMS = ('Linux', 'Windows')    # Supported Operating Systems
ERROR_CODES = {300: "PLATFORM_INVALID",
               400: "NETWORK_ACCESS_FAILED",
               500: "UNKNOWN_ERROR"
              }

API_ENDPOINT = 'https://api.intellivoid.net/openblu/v1'  # You may setup your own API endpoint if you wish


def get_server_info(uuid: str, key: str, verbose: bool = False):
    """Fetches a single OpenVPN server from the OpenBlu API, given its unique ID

       :param uuid: The unique ID of the desired server
       :type uuid: str
       :param key: The OpenBlu API key
       :type key: str
       :param verbose: If ``True``, make output verbose, default to ``False``
       :type verbose: bool, optional
       :returns: A dictionary containing the requested info, or ``None`` if the server doesn't exist
       :rtype: dict, None
    """

    link = API_ENDPOINT + "/servers/get"
    if verbose:
        print(f"API key is {key}")
        print(f"Fetching from {link}...")
    post_data = {}
    post_data["access_key"] = key
    post_data["id"] = uuid
    response = requests.post(link, data=post_data)
    try:
        data = json.loads(response.content)
    except json.JSONDecoder.JSONDecodeError as decode_error:
        print(f"Error: The API did not send a properly formatted response, error: {decode_error}")
        exit(decode_error)
    return data


def fetch_servers(endpoint: str = API_ENDPOINT, filter_by: Union[None, tuple] = None, order_by: Union[None, str] = None, sort_by: Union[None, str] = None, verbose: bool = True, key: Union[None, str] = None):
    """Fetches OpenVPN servers from the OpenBlu API

       :param endpoint: The API endpoint to contact and fetch the servers list from, defaults to 'https://api.intellivoid.info/openblu/v1'
       :type endpoint: str, None, optional
       :param filter_by: If not ``None``, filter the results by the given country, defaults to ``None``
       :type filter_by: tuple, None, optional
       :param order_by: If not ``None``, order the results by this order. It can either be ``'ascending'`` or ``'descending'``, defaults to ``None``
       :type order_by: str, None, optional
       :param sort_by: Sorts the list by the given condition, defaults to ``None`` (no sorting)
       :type sort_by: str, None, optional
       :param verbose: If ``True``, make the output verbose, default to ``False``
       :type verbose: bool, optional
       :param key: The OpenBlu API key, defaults to ``None``
       :type key: str, None, optional
       :returns servers_list: The list of available servers with the specified filters
       :rtype servers_list: dict
    """

    link = API_ENDPOINT + "/servers/list"
    if verbose:
        print(f"API key is {key}")
        print(f"Fetching from {link}...")
    post_data = {}
    post_data["access_key"] = key
    if filter_by[0]:
        post_data["by"] = filter_by[1]
        post_data["filter"] = filter_by[0]
    if order_by:
        post_data["order_by"] = order_by
    if sort_by:
        post_data["sort_by"] = sort_by
    response = requests.post(link, data=post_data)
    try:
        data = json.loads(response.content)
    except json.JSONDecoder.JSONDecodeError as decode_error:
        print(f"Error: The API did not send a properly formatted response, error: {decode_error}")
        exit(decode_error)
    return data


def openblu(parsed_args):
    """Main entry point for the OpenBlu client UI

       :param parsed_args: The result of ``argparse.ArgumentParser().parse_args()``
       :type parsed_args: class: Namespace
    """

    if parsed_args.verbose:
        print(f"Platform is: '{platform.system()}'")
    api_key = parsed_args.key
    if parsed_args.fetch_servers:
        if parsed_args.verbose:
            print(f"Fetching available VPN servers from {API_ENDPOINT}\nCountry: {'Any' if not parsed_args.filter_by else parsed_args.filter_by}\nOrder: {None if not parsed_args.order_by else parsed_args.order_by}\nSorted by: {None if not parsed_args.sort_by else parsed_args.sort_by}")
        servers_list = fetch_servers(API_ENDPOINT, (parsed_args.filter_by, parsed_args.filter), parsed_args.order_by, parsed_args.sort_by, parsed_args.verbose, api_key)
        if not servers_list['success']:
            print(f"Error: Something went wrong when retrieving the servers! More details below\nHTTP Response Code: {servers_list['response_code']}\nAPI Error Code: {servers_list['error']['error_code']}\nAPI Error Message: {servers_list['error']['message']}\nAPI Error Type: {servers_list['error']['type']}")
        else:
            if parsed_args.verbose:
                print(f"Success! Retrieved {len(servers_list['servers'])} servers matching the provided filters")
            servers = PrettyTable()
            if parsed_args.verbose:
                servers.field_names = ["ID", "Hostname", "Country", "Country Short", "Score", "Ping (ms)", "Active Sessions", "Total Sessions", "Last Updated", "Created"]
            else:
                servers.field_names = ["ID", "Hostname", "Country", "Ping (ms)", "Active Sessions", "Last Updated"]
            for x in range(parsed_args.limit):
                if not servers_list['servers']:
                    break
                try:
                    server = servers_list['servers'].pop(x)
                except IndexError:
                    break
                server_id = server['id']
                host_name = server['host_name']
                country = server['country']
                country_short = server['country_short']
                score = server['score']
                ping = server['ping']
                sessions = server['sessions']
                total_sessions = server['total_sessions']
                last_updated = datetime.utcfromtimestamp(server['last_updated']).strftime('%Y-%m-%d %H:%M:%S %p')
                created = datetime.utcfromtimestamp(server['created']).strftime('%Y-%m-%d %H:%M:%S')
                if parsed_args.verbose:
                    servers.add_row([server_id, host_name, country, country_short, score, ping, sessions, total_sessions, last_updated, created])
                else:
                    servers.add_row([server_id, host_name, country, ping, sessions, last_updated])
            print(servers)
    elif parsed_args.set_access_key:
        try:
            access_key = input("Type here your access key: ")
        except (EOFError, KeyboardInterrupt):
            print()
            exit(1)
        if not access_key:
            print("Error: Access Key cannot be blank!")
            exit(1)
        try:
            with open(os.path.join(os.getcwd(), "openblu.key"), "w") as access_file:
                access_file.write(access_key)
        except PermissionError:
            print("Error: Could not create the configuration file due to a permission issue, please consider using the --key option or provide read/write access to the current working directory")
    elif parsed_args.info:
        server = get_server_info(parsed_args.info, api_key, parsed_args.verbose)
        if server['success']:
            if parsed_args.verbose:
                print(f"Success, creating .ovpn file...")
            try:
                with open(os.path.join(os.getcwd(), f"{server['server']['id']}.ovpn"), "w") as access_file:
                    access_file.write(server['server']['openvpn']['ovpn_configuration'])
            except PermissionError:
                print("Error: Could not create the .ovpn file for the server, please make sure that the program has read/write access to the current workdir")
                exit(1)
        elif server['response_code'] == 404:
            print("Error: A VPN Server with that ID doesn't exist")
            exit(1)
        elif server['response_code'] not in (200, 404):
            print(f"Error: Something went wrong when retrieving the servers! More details below\nHTTP Response Code: {server['response_code']}\nAPI Error Code: {server['error']['error_code']}\nAPI Error Message: {server['error']['message']}\nAPI Error Type: {server['error']['type']}")
            exit(ERROR_CODES[500])
    elif parsed_args.country:
        if parsed_args.connect_best:
            print(f"Looking for the best server in selected country...")
            servers_list = fetch_servers(API_ENDPOINT, ("country", parsed_args.country), parsed_args.order_by, parsed_args.sort_by, parsed_args.verbose, api_key)
            if servers_list['success']:
                if servers_list['servers']:
                    server = max(servers_list['servers'], key=lambda x: x['last_updated'])
                else:
                    server = None
            else:
                print(f"Error: Something went wrong when retrieving the servers! More details below\nHTTP Response Code: {servers_list['response_code']}\nAPI Error Code: {servers_list['error']['error_code']}\nAPI Error Message: {servers_list['error']['message']}\nAPI Error Type: {servers_list['error']['type']}")
                exit(ERROR_CODES[500])
        else:
            servers_list = fetch_servers(verbose=parsed_args.verbose)
            if servers_list['success']:
                if servers_list['servers']:
                    server = servers_list['servers'][0]
                else:
                    server = None
        if not server:
            print("Error: No server found with given parameters")
        else:
            print("Connecting to found server...")
            if parsed_args.verbose:
                print("Retrieving info about the server...")
            server = get_server_info(server['id'], api_key, parsed_args.verbose)
            if server['success']:
                if parsed_args.verbose:
                    print(f"Success, creating .ovpn file...")
                try:
                    with open(os.path.join(os.getcwd(), f"{server['server']['id']}.ovpn"), "w") as access_file:
                        access_file.write(server['server']['openvpn']['ovpn_configuration'])
                except PermissionError:
                    print("Error: Could not create the .ovpn file for the server, please make sure that the program has read/write access to the current workdir")
                    exit(1)
                if parsed_args.verbose:
                    print(f"Spawning subprocess for OpenVPN with file '{server['id']}'")
                process = subprocess.run(f"nohup openvpn --config {server['server']['id']}.ovpn &", shell=True)
                if process.returncode != 0:
                    print(f"Error: The OpenVPN process exited with error: {process.returncode}")
            else:
                print(f"Error: Something went wrong when retrieving the servers! More details below\nHTTP Response Code: {server['response_code']}\nAPI Error Code: {server['error']['error_code']}\nAPI Error Message: {server['error']['message']}\nAPI Error Type: {server['error']['type']}")
                exit(ERROR_CODES[500])


def setup_args(system: str):
    """Performs the necessary setup for the ``argparse`` module and does some checks on the arguments

       :param system: The qualified name of the current OS
       :type system: str
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="The API Key for Intellivoid API", type=str)
    parser.add_argument("-b", "--connect-best", help="This flag tells the client to search for the best server to connect to", action='store_true')
    parser.add_argument("-c", "--country", help="Connects to the first available server in the chosen country, if any", type=str)
    parser.add_argument("-f", "--fetch-servers", help='Fetches all available OpenBlu VPN servers and shows them to the user', action='store_true')
    parser.add_argument("-i", "--info", help='Fetches specific information about a server, given its unique ID. The .ovpn configuration is saved in the current workdir', type=str)
    parser.add_argument("--filter-by", help='Filters the retrieved servers list by country or country_short, requires --filter', type=str, choices=('country', 'country_short'))
    parser.add_argument("--filter", help='The value to filter by, e.g. japan, thailand, etc. Requires --filter-by')
    parser.add_argument("-o", "--order-by", help="Orders the results by score, ping, sessions, total_sessions, last_updated and created", choices=("score", "ping", "sessions", "total_sessions", "last_updated", "created"), type=str)
    parser.add_argument("-s", "--sort-by", help='Sorts the ordered results by descending or ascending order', choices=("ascending", "descending"), type=str)
    parser.add_argument("-v", "--verbose", help='Make the output verbose', action='store_true')
    parser.add_argument("-l", "--limit", help='Sets the limit of servers that are printed to stdout, defaults to 5. Only applicable when fetching servers', type=int, default=5)
    parser.add_argument("--set-access-key", help='Saves your access key for future use, please note that if a config file is present in the current workdir, the --key option is ignored', action='store_true')
    args = parser.parse_args()
    if os.path.isfile(os.path.join(os.getcwd(), "openblu.key")):
        try:
            with open(os.path.join(os.getcwd(), "openblu.key"), "r") as access_file:
                access_key = access_file.readline()
        except PermissionError:
            print("Error: Could not read configuration file due to a permission issue, please consider using the --key option or provide read/write access to the current working directory")
            exit(1)
        if access_key:
            args.key = access_key
        else:
            print("Error: The configuration file is empty, try running openblu --set-access-key again or use the --key option")
            exit(1)
    if args.filter_by:
        if not args.filter:
            print("Error: --filter-by requires --filter!")
            exit(1)
    elif args.filter:
        if not args.filter_by:
            print("Error: --filter requires --filter-by!")
    openblu(args)


def get_platform():
    """Ran on startup, determines if the current platform is supported or not

        :returns: The value of ``platform.system()``, if the platform is supported
        :rtype: str
    """

    if platform.system() not in SYSTEMS:
        print("Error: Your platform is either unsupported or could not be determined, exiting")
        exit(ERROR_CODES[300])
    return platform.system()


if __name__ == "__main__":
    setup_args(get_platform())
