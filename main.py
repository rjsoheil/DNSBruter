import argparse
import signal
import sys
from tools import StaticBrute, DynamicBrute, DataBaseHandler
from config import common_args
from colorama import Fore

def signal_handler(sig, frame):
    print(f"\n{Fore.YELLOW}[!] Process interrupted by user. Exiting gracefully...{Fore.RESET}")
    sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description=f"{Fore.LIGHTGREEN_EX}dnsBruter\n{Fore.WHITE}Creator: {Fore.LIGHTCYAN_EX}rjsoheil {Fore.RED}")
    parser.add_argument("--domain", "-d", type=str, help=f"Target domain in the format {Fore.GREEN}example.com{Fore.WHITE}")
    parser.add_argument("--list-subs", "-ls", type=str, default=False, help="File containing list of subdomains to dynamic brute force")
    parser.add_argument("--mode", "-m", required=True, type=str, help="Mode of DNS Brute-Force (static|dynamic)", choices=['static', 'dynamic'])
    parser.add_argument("--wordlist", "-w", required=True, type=str, help="Wordlist to perform static DNS Brute-Force")
    parser.add_argument("--resolvers", "-r", type=str, help="File containing list of resolvers for enumeration")
    parser.add_argument("--path-massdns", "-pm", type=str, help="Path to the massdns binary")
    parser.add_argument("--out-put", "-o", default=False, action="store_true", help="File to write output to (optional)")
    parser.add_argument("--insert", "-i", default=False, action="store_true", help="Inserting the new non-repetitive subdomains in the database")
    parser.add_argument("--default", default=False, action="store_true", help="Using defualt configuration in the config file")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    target = args.domain
    mode = args.mode

    try:
        signal.signal(signal.SIGINT, signal_handler)
        if len(sys.argv) > 4:
            if args.default:
                args.resolvers = common_args["resolvers"]
                args.path_massdns = common_args["path_massdns"]
            if target:
                if mode == "static":
                    brute_forcer = StaticBrute(target, args.wordlist, args.resolvers, args.path_massdns, args.out_put)
                    result = brute_forcer.start_brute_force()
                    if not args.insert:
                        print("\n".join(result))
                    elif result and args.insert:
                        DbHandler = DataBaseHandler(target, result)
                        DbHandler.insert_into_database()

                elif mode == "dynamic" and args.list_subs: # Done
                    brute_forcer = DynamicBrute(target, args.wordlist, args.resolvers, args.path_massdns, args.list_subs, args.out_put)
                    brute_forcer.generate_dy_wordlist()
                    result = brute_forcer.start_brute_force()
                    if not args.insert:
                        print("\n".join(result))
                    elif result and args.insert:
                        DbHandler = DataBaseHandler(target, result)
                        DbHandler.insert_into_database()

                elif mode == "dynamic" and not args.list_subs: # dynamic brute force on the one domain
                    brute_forcer = DynamicBrute(target, args.wordlist, args.resolvers, args.path_massdns, args.list_subs, file_path =f"/tmp/{target}_one_target.txt", file_output=args.out_put)
                    file_path = f"/tmp/{target}_one_target.txt"
                    brute_forcer.generate_one_domain_file()
                    brute_forcer.generate_dy_wordlist()
                    brute_forcer.remove_one_domain_file()
                    result = brute_forcer.start_brute_force()
                    if not args.insert:
                        print("\n".join(result))
                    elif result and args.insert:
                        DbHandler = DataBaseHandler(target, result)
                        DbHandler.insert_into_database()
        else:
            print("Please provide necessary arguments!")
    except Exception as e:
        print(f"Error: {e}")