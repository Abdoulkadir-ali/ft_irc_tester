#!/usr/bin/env python3
"""
Testeur IRC modulaire pour ft_irc.
Configure le serveur, charge les suites de tests et orchestre l'exécution.
Usage :
  python3 tests/run_tests.py [password] [--verbose[=True/3/False]] [--binary [path]]
"""
import os
import sys
import argparse

# Ajouter le dossier des tests au path pour les imports locaux
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from server_manager import IRCServerManager
from framework import TestRunner
from printer import IRCPrinter
import suites  # Déclenche l'enregistrement des tests

def parse_verbose(val):
    val_str = str(val).strip().lower()
    if val_str in ("false", "0", "none"):
        return 0
    elif val_str in ("true", "1"):
        return 1
    elif val_str == "3":
        return 3
    else:
        # Si une autre valeur est passée (par exemple --verbose sans valeur),
        # par défaut à la verbosité de niveau 1
        return 1

def main():
    parser = argparse.ArgumentParser(description="Testeur IRC modulaire pour ft_irc.")
    parser.add_argument("password", nargs="?", default="secret", 
                        help="Mot de passe du serveur IRC (défaut: 'secret')")
    parser.add_argument("--verbose", nargs="?", const="True", default="False", 
                        help="Niveau de verbosité : False, True (niveau 1), ou 3 (niveau maximum)")
    parser.add_argument("--binary", default=None, 
                        help="Chemin explicite vers le binaire 'ircserv'")

    args = parser.parse_args()

    verbose_level = parse_verbose(args.verbose)
    
    printer = IRCPrinter(verbose=verbose_level)
    server_mgr = IRCServerManager(password=args.password, binary_path=args.binary, printer=printer)
    runner = TestRunner(server_mgr, printer=printer)
    
    success = runner.run_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
