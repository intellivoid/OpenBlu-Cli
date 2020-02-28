# OpenBlu-Cli
Official OpenBlu command-line interface to fetch and list available servers, filter them and connect to them with ease


# Usage

```    
usage: python3 openblu.py [-h] [--key KEY] [-b] [-c COUNTRY] [-f] [-i INFO] [--filter-by {country,country_short}] [--filter FILTER]
                  [-o {score,ping,sessions,total_sessions,last_updated,created}] [-s {ascending,descending}] [-v] [-l LIMIT] [--set-access-key]

optional arguments:
  -h, --help            show this help message and exit
  --key KEY             The API Key for Intellivoid API
  -b, --connect-best    This flag tells the client to search for the best server to connect to
  -c COUNTRY, --country COUNTRY
                        Connects to the first available server in the chosen country, if any
  -f, --fetch-servers   Fetches all available OpenBlu VPN servers and shows them to the user
  -i INFO, --info INFO  Fetches specific information about a server, given its unique ID. The .ovpn configuration is saved in the current workdir
  --filter-by {country,country_short}
                        Filters the retrieved servers list by country or country_short, requires --filter
  --filter FILTER       The value to filter by, e.g. japan, thailand, etc. Requires --filter-by
  -o {score,ping,sessions,total_sessions,last_updated,created}, --order-by {score,ping,sessions,total_sessions,last_updated,created}
                        Orders the results by score, ping, sessions, total_sessions, last_updated and created
  -s {ascending,descending}, --sort-by {ascending,descending}
                        Sorts the ordered results by descending or ascending order
  -v, --verbose         Make the output verbose
  -l LIMIT, --limit LIMIT
                        Sets the limit of servers that are printed to stdout, defaults to 5. Only applicable when fetching servers
  --set-access-key      Saves your access key for future use, please note that if a config file is present in the current workdir, the --key option is
                        ignored
```

## Example: Retrieve up to 10 servers
  
`python3 openblu.py -f --limit 10 --key YOUR KEY HERE`


## Example: Save your Access Key

```
python3 openblu.py --set-access-key

Type here your access key: KEY HERE
```

## Example: retrieve the ovpn file of a server

`python3 openblu.py -i ID`


For more info, check [OpenBlu's Documentation](https://gist.github.com/Netkas/6d09bd76ad8a6eaee6a6229b17eb373f)

