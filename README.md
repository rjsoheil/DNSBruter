# DNSBruter
This tool accurately uses both static and dynamic modes for subdomain brute forcing and stores it in its database (optional).
  - Static
  - Dynamic
    - Single subdomain
    - List of subdomains
  - New data storage (mongo database)

## Preview
![image](https://github.com/user-attachments/assets/805ca667-9106-4d00-bc68-8ce8c2b3f1cf)

## Installation
```
git clone https://github.com/rjsoheil/DNSBruter.git
pip install -r requirements.txt
cat script.txt >> ~/.zshrc OR cat script.txt >> ~/.bashrc
```
To use this tool, you must have the following tools installed:
  - [shuffledns](https://github.com/projectdiscovery/shuffledns/)
  - [massdns](https://github.com/blechschmidt/massdns/)
  - [dnsgen](https://github.com/AlephNullSK/dnsgen/)

## Usage
### Static Brute Force
- Command:
  `python3 main.py --mode static -w words.txt -d target.com --path-massdns /usr/bin/massdns -r ~/resolvers`
### Dynamic Brute Force
  - On the list of subdomains:
    `python3 main.py --mode dynamic --list-subs target-subs.txt -w words-merged.txt -d target.com -pm /usr/bin/massdns -r ~/resolvers`
  - On the single subdomain:
    `python3 main.py --mode dynamic -w words-merged.txt -d api.target.com -pm /usr/bin/massdns -r ~/resolvers`

### Data storage
  This tool uses Mongo database for data storage
  - Switch: `--insert`
    Stored data:
      - Subdomain
      - Data added
      - Mode (The mode in which the tool found this subdomain)

### Get a list of subdomains
  - Filter by mode
    `python3 main.py --get -d target.com -m static`
  - Without filtering
    `python3 main.py -g -d target.com`
