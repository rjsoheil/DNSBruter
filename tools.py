import subprocess
import os
from colorama import Fore
from pymongo import MongoClient
from datetime import datetime

class DataBase:
    def __init__(self, target, subdomains, mode):
        self.target = target
        self.subdomains = subdomains
        self.mode = mode

    def insert_into_database(self):
        raise NotImplementedError("This method should be implemented by subclasses")

class DataBaseHandler(DataBase):
    def insert_into_database(self):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client['dns_brute_force']
            collection_name = self.target.replace('.', '_')
            collection = db[collection_name]
            now = datetime.now()

            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"{Fore.GREEN}\n[+] Collection '{Fore.RED}{collection_name}{Fore.GREEN}' has been created in the {Fore.RED}dns_brute_force {Fore.GREEN}database.{Fore.RESET}")

            existing_subdomains = collection.find({"subdomain": {"$in": self.subdomains}})
            existing_subdomains = [item['subdomain'] for item in existing_subdomains]
            new_subdomains = [subdomain for subdomain in self.subdomains if subdomain not in existing_subdomains]
            if new_subdomains:
                data = [{'subdomain': subdomain, 
                         'date_added': now.strftime("%Y-%m-%d %H:%M:%S"),
                         'mode':self.mode} 
                         for subdomain in new_subdomains]
                collection.insert_many(data)
                print(f"Inserting {Fore.GREEN}{len(new_subdomains)}{Fore.RESET} new subdomains into the {Fore.GREEN}{self.target}{Fore.RESET} collection in the database...")
                for subdomain in new_subdomains:
                    print(f"\t{Fore.GREEN}[+] Subdomain: {Fore.CYAN}{subdomain}{Fore.GREEN} inserted successfully.{Fore.WHITE}")
            else:
                print(f"{Fore.YELLOW}[-] No new subdomains to insert. All subdomains already exist in the database. [-]{Fore.RESET}")

        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}")

    def get_subdomains(self):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client['dns_brute_force']
            collection_name = self.target.replace('.', '_')
            collection = db[collection_name]

            if collection_name in db.list_collection_names():
                if self.mode:
                    result = collection.find({"mode":self.mode}, {"subdomain": 1, "date_added":1})
                    subdomains = [(record["subdomain"], record["date_added"]) for record in result]
                else:
                    result = collection.find({}, {"subdomain": 1, "date_added":1, "mode":1})
                    subdomains = [(record["subdomain"], record["date_added"], record["mode"]) for record in result]

                return subdomains

            else:
                print(f"{Fore.LIGHTRED_EX}[-] Collection '{collection_name}' does not exist.\n{Fore.WHITE}")
                return []

        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e} {Fore.YELLOW}(){Fore.WHITE}")
            return []

class DNSBruter:
    def __init__(self, target, wordlist, resolvers, massdns_path, file_output=False):
        self.target = target
        self.wordlist = wordlist
        self.resolvers = resolvers
        self.massdns_path = massdns_path
        self.file_output = file_output

    def start_brute_force(self):
        raise NotImplementedError("This method should be implemented by subclasses")

class StaticBrute(DNSBruter):
    def start_brute_force(self):
        print(f"{Fore.GREEN}[X]\t{Fore.RED}<FUZZ>{Fore.LIGHTRED_EX}.{self.target}{Fore.GREEN}     [X]{Fore.RESET}")
        command = [
            'shuffledns', '-silent',
            '-d', self.target,
            '-w', self.wordlist,
            '-r', self.resolvers,
            '-m', self.massdns_path,
            '-mode', 'bruteforce'
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                return result.stdout.strip().split('\n')
            else:
                print(f"{Fore.RED}[-]\tOutput is empty!    [-]{Fore.RESET}")
                return []

        except subprocess.CalledProcessError as e:
            print(f"{Fore.LIGHTRED_EX}Command failed with exit code {e.returncode}: {e}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Unexpected error occurred: {e}{Fore.RESET}")

class DynamicBrute(DNSBruter):
    def __init__(self, target, wordlist, resolvers, massdns_path, subdomain_list, file_path, file_output=""):
        super().__init__(target, wordlist, resolvers, massdns_path, file_output)
        self.subdomain_list = subdomain_list
        self.file_path = file_path
        # self.one_domain = one_domain

    def generate_dy_wordlist(self):
        try:
            print(f"{Fore.LIGHTGREEN_EX}[+] Start generating dynamic wordlist ... [+]")
            if self.subdomain_list:
                command = f"zsh -c 'source ~/.zshrc && wldns_subexpander {self.subdomain_list} {self.wordlist} {self.target}'"
            else:
                command = f"zsh -c 'source ~/.zshrc && wldns_subexpander {self.file_path} {self.wordlist} {self.target}'"
            subprocess.run(command, shell=True, check=True)

            file_name = self.target + "-wl-dnsbrute.txt"
            if os.path.exists(file_name):
                print(f"{Fore.LIGHTGREEN_EX}[+] Dynamic Wordlist created successfully: {Fore.LIGHTRED_EX}{file_name}{Fore.RESET}\n")
            else:
                print(f"{Fore.RED}[-] Dynamic Wordlist could not be created{Fore.RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error: {e}{Fore.WHITE}")

    def generate_one_domain_file(self): # Usefull for dynamic bruteforce on the one domain
        try:
            command = f"zsh -c 'echo {self.target} > /tmp/{self.target}_one_target.txt'"
            subprocess.run(command, shell=True, check=True)
            file_path = f"/tmp/{self.target}_one_target.txt"
            if os.path.exists(file_path):
                print(f"{Fore.LIGHTGREEN_EX}[+] The file '{Fore.LIGHTRED_EX}{file_path}{Fore.LIGHTGREEN_EX}' created.{Fore.WHITE}")
            else:
                print(f"{Fore.LIGHTRED_EX}[+] The file '{Fore.LIGHTRED_EX}{file_path}{Fore.LIGHTGREEN_EX}' does not exist.{Fore.WHITE}")

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error: {e}{Fore.WHITE}")

    def remove_one_domain_file(self): # Usefull for dynamic bruteforce on the one domain
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                print(f"{Fore.LIGHTGREEN_EX}[+] The file '{Fore.LIGHTRED_EX}{self.file_path}{Fore.LIGHTGREEN_EX}' has been deleted successfully.{Fore.WHITE}")
            else:
                print(f"{Fore.LIGHTRED_EX}[-] The file '{self.file_path}{Fore.LIGHTGREEN_EX}' does not exist.{Fore.WHITE}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error: {e}{Fore.WHITE}")

    def start_brute_force(self):
        print(f"{Fore.LIGHTGREEN_EX}\t\t\t[X]\t{Fore.LIGHTRED_EX}<RESOLVING>{Fore.RED}.{self.target}{Fore.GREEN}\t[X]{Fore.WHITE}")
        if self.subdomain_list:
            command = [
                'shuffledns', '-silent',
                '-d', self.target,
                '-l', f'{self.target}-wl-dnsbrute.txt',
                '-r', self.resolvers,
                '-m', self.massdns_path,
                '-mode', 'resolve'
            ]
        else:
            command = [
                'shuffledns', '-silent',
                '-d', self.target,
                '-l', f'/tmp/{self.target}_one_target.txt',
                '-r', self.resolvers,
                '-m', self.massdns_path,
                '-mode', 'resolve'
            ]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                return result.stdout.strip().split('\n')
            else:
                print(f"{Fore.RED}[-]\tOutput is empty!    [-]{Fore.RESET}")
                return []
        except subprocess.CalledProcessError as e:
            print(f"{Fore.LIGHTRED_EX}Command failed with exit code {e.returncode}: {e}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Unexpected error occurred: {e}{Fore.RESET}")