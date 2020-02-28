import argparse
import requests
import platform
from typing import Union
import json


SYSTEMS = ('Linux', 'Windows')    # Supported Operating Systems
ERROR_CODES = {300: "PLATFORM_INVALID",
               400: "NETWORK_ACCESS_FAILED",
               500: "UNKNOWN_ERROR"
              }

API_ENDPOINT = 'https://api.intellivoid.info/openblu/v1'  # You may setup your own API endpoint if you wish


def fetch_servers(endpoint: str = API_ENDPOINT, filter_by: Union[None, str] = None, order_by: Union[None, str] = None, sort_by: Union[None, str] = None, verbose: bool = True, key: Union[None, str] = None):
    """Fetches OpenVPN servers from the OpenBlu API

       :param endpoint: The API endpoint to contact and fetch the servers list from, defaults to 'https://api.intellivoid.info/openblu/v1'
       :type endpoint: str, None, optional
       :param filter_by: If not ``None``, filter the results by the given country, defaults to ``None``
       :type filter_by: str, None, optional
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
    link += f"?access_key={key}"
    if filter_by:
        link += "&filter=true"
    if order_by:
        link += "&order_by={order_by}"
    if sort_by:
        link += "&sort_by={sort_by}"
    response = requests.get(link)
    try:
        data = json.loads(response.content)
    except json.JSONDecoder.JSONDecodeError as decode_error:
        print(f"The API did not send a properly formatted response, error: {decode_error}")
    return data


def openblu_windows(parsed_args):
    """Main entry point for Windows-specific openblu client UI

       :param parsed_args: The result of ``argparse.ArgumentParser().parse_args()
       :type parsed_args: class: Namespace
    """

    print("Platform is: 'Windows'")


def openblu_linux(parsed_args):
    """Main entry point for Linux-specific openblu client UI

       :param parsed_args: The result of ``argparse.ArgumentParser().parse_args()``
       :type parsed_args: class: Namespace
    """

    if parsed_args.verbose:
        print("Platform is: 'Linux'")
    api_key = parsed_args.key
    if parsed_args.fetch_servers:
        if parsed_args.verbose:
            print(f"Fetching available VPN servers from {API_ENDPOINT}\nCountry: {'Any' if not parsed_args.filter_by else parsed_args.filter_by}\nOrder: {None if not parsed_args.order_by else parsed_args.order_by}\nSorted by: {None if not parsed_args.sort_by else parsed_args.sort_by}")
        servers_list = fetch_servers(API_ENDPOINT, parsed_args.filter_by, parsed_args.order_by, parsed_args.sort_by, parsed_args.verbose, api_key)
        if not servers_list['success']:
            print(f"Something went wrong when retrieving the servers! More details below\nHTTP Response Code: {servers_list['response_code']}\nAPI Error Code: {servers_list['error']['error_code']}\nAPI Error Message: {servers_list['error']['message']}\nAPI Error Type: {servers_list['error']['type']}")


def setup_args(system: str):
    """Performs the necessary setup for the ``argparse`` module

       :param system: The qualified name of the current OS
       :type system: str
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("key", help="The API Key for Intellivoid API", type=str)
    parser.add_argument("-b", "--connect-best", help="This flag tells the client to search for the best server to connect to", action='store_true')
    parser.add_argument("-c", "--country", help="Tries to search a server in the specified location, or falls back to a random one if a server in the specified country cannot be found", type=str)
    parser.add_argument("-f", "--fetch-servers", help='Fetches all available OpenBlu VPN servers and shows them to the user', action='store_true')
    parser.add_argument("-i", "--info", help='Fetches specific information about a server, given its unique ID', type=str)
    parser.add_argument("--filter-by", help='Filters the retrieved servers list by the given country (or country_short, e.g. IT for Italy)', type=str)
    parser.add_argument("-o", "--order-by", help="Orders the results by score, ping, sessions, total_sessions, last_updated and created", choices=("score", "ping", "sessions", "total_sessions", "last_updated", "created"), type=str)
    parser.add_argument("-s", "--sort-by", help='Sorts the ordered results by descending or ascending order', choices=("ascending", "descending"), type=str)
    parser.add_argument("-v", "--verbose", help='Make the output verbose', action='store_true')
    platforms_specific[system](parser.parse_args())  # Calls the respective platform-specific function


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
    platforms_specific = {"Windows": openblu_windows, "Linux": openblu_linux}
    setup_args(get_platform())
