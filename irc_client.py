import socket
import time

class IRCClient:
    def __init__(self, nick, host, port):
        self.nick = nick
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2.0)
        self.buf = ""
        self.lines = []
        self.history = []  # List of tuples (timestamp, type, content) where type is "SEND" or "RECV"

    def connect(self):
        self.sock.connect((self.host, self.port))
        self._log("CONN", f"Connected to {self.host}:{self.port}")

    def _log(self, type_, content):
        self.history.append((time.time(), type_, content))

    def send(self, command):
        self.sock.sendall((command + "\r\n").encode())
        self._log("SEND", command)

    def recv_lines(self, timeout=1.0):
        self.sock.settimeout(timeout)
        result = []
        try:
            while len(result) < 30:
                data = self.sock.recv(4096).decode(errors="replace")
                if not data:
                    self._log("RECV_EOF", "Server closed connection (received empty bytes)")
                    break
                self.buf += data
                while "\n" in self.buf:
                    line, self.buf = self.buf.split("\n", 1)
                    line = line.rstrip("\r")
                    result.append(line)
                    self.lines.append(line)
                    self._log("RECV", line)
        except socket.timeout:
            pass
        return result

    def wait(self, kw, timeout=2.0):
        deadline = time.time() + timeout
        self.sock.settimeout(timeout)
        while time.time() < deadline:
            try:
                # We do recv chunk by chunk to process lines dynamically
                data = self.sock.recv(4096).decode(errors="replace")
                if not data:
                    self._log("RECV_EOF", "Server closed connection while waiting")
                    break
                self.buf += data
                while "\n" in self.buf:
                    line, self.buf = self.buf.split("\n", 1)
                    line = line.rstrip("\r")
                    self.lines.append(line)
                    self._log("RECV", line)
                    if kw in line:
                        return line
            except socket.timeout:
                break
        return None

    def register(self, password):
        self.send(f"PASS {password}")
        self.send(f"NICK {self.nick}")
        self.send(f"USER {self.nick} 0 * :{self.nick}")
        return self.wait(" 001 ")

    def close(self):
        try:
            self.send("QUIT :bye")
        except Exception:
            pass
        self.sock.close()
        self._log("CONN", "Socket closed")
        
    def get_traffic_log(self):
        """Returns a string representing the formatted traffic history."""
        output = []
        for ts, type_, content in self.history:
            time_str = time.strftime('%H:%M:%S', time.localtime(ts))
            if type_ == "CONN":
                output.append(f"[{time_str}] [SYSTEM] {content}")
            elif type_ == "SEND":
                output.append(f"[{time_str}]   >>>   {content}")
            elif type_ == "RECV":
                output.append(f"[{time_str}]   <<<   {content}")
            elif type_ == "RECV_EOF":
                output.append(f"[{time_str}] [SYSTEM] {content}")
        return "\n".join(output)
