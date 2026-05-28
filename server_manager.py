import socket
import time
import subprocess
import os
import sys
from printer import IRCPrinter

class IRCServerManager:
    def __init__(self, password="secret", binary_path=None, printer=None):
        self.password = password
        self.host = "127.0.0.1"
        self.port = 0
        self.proc = None
        self.printer = printer or IRCPrinter()
        
        if binary_path is None:
            self.binary = self._find_binary()
        else:
            self.binary = os.path.realpath(binary_path)

        if not self.binary or not os.path.isfile(self.binary):
            self.printer.print_error(f"binaire 'ircserv' introuvable ({self.binary or 'Non spécifié'}) — lancez 'make' d'abord.")
            sys.exit(1)

    def _find_binary(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(script_dir, "..", "ircserv"),
            os.path.join(script_dir, "ircserv"),
            "./ircserv",
        ]
        return next((os.path.realpath(p) for p in candidates if os.path.isfile(p)), None)

    @staticmethod
    def find_free_port():
        """Asks the kernel for a free TCP port, then releases it."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", 0))
            return s.getsockname()[1]

    def start(self):
        self.port = self.find_free_port()
        self.proc = subprocess.Popen(
            [self.binary, str(self.port), self.password],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        
        # Wait up to 5 seconds for the server to accept connections
        deadline = time.time() + 5.0
        while time.time() < deadline:
            try:
                with socket.create_connection((self.host, self.port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            self.printer.print_error(f"serveur non accessible sur {self.host}:{self.port} — abandon.")
            self.stop()
            sys.exit(1)
        
        return self.port

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            except Exception:
                pass
