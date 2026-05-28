import os
import json

DEFAULT_CONFIG = {
  "use_colors": True,
  "colors": {
    "green": "\u001b[92m",
    "red": "\u001b[91m",
    "yellow": "\u001b[93m",
    "blue": "\u001b[94m",
    "magenta": "\u001b[95m",
    "cyan": "\u001b[96m",
    "bold": "\u001b[1m",
    "reset": "\u001b[0m"
  },
  "symbols": {
    "pass": "🟢",
    "fail": "🔴",
    "run": "⏳"
  },
  "layout": {
    "section_width": 68,
    "summary_width": 60,
    "bar_width": 30
  }
}

class IRCPrinter:
    def __init__(self, verbose=0, config_path=None):
        self.verbose = verbose
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "printer_config.json"
        )
        self.config = self._load_config()
        self._init_styles()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=2)
            except Exception:
                pass
            return DEFAULT_CONFIG

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG

    def _init_styles(self):
        use_colors = self.config.get("use_colors", True)
        colors = self.config.get("colors", DEFAULT_CONFIG["colors"])
        
        # Color codes helper
        def get_color_code(name):
            return colors.get(name, "") if use_colors else ""

        self.G = get_color_code("green")
        self.R = get_color_code("red")
        self.Y = get_color_code("yellow")
        self.B = get_color_code("blue")
        self.M = get_color_code("magenta")
        self.C = get_color_code("cyan")
        self.BO = get_color_code("bold")
        self.X = get_color_code("reset")

        symbols = self.config.get("symbols", DEFAULT_CONFIG["symbols"])
        self.sym_pass = symbols.get("pass", "🟢")
        self.sym_fail = symbols.get("fail", "🔴")
        self.sym_run = symbols.get("run", "⏳")

        layout = self.config.get("layout", DEFAULT_CONFIG["layout"])
        self.section_width = layout.get("section_width", 68)
        self.summary_width = layout.get("summary_width", 60)
        self.bar_width = layout.get("bar_width", 30)

    def print_section(self, phase_name):
        """Prints a styled header for a test phase."""
        border = "┌" + "─" * self.section_width + "┐"
        padding = (self.section_width - len(phase_name)) // 2
        header_line = "│" + " " * padding + phase_name + " " * (self.section_width - len(phase_name) - padding) + "│"
        bottom = "└" + "─" * self.section_width + "┘"
        print(f"\n{self.BO}{self.B}{border}\n{header_line}\n{bottom}{self.X}")

    def format_traffic_line(self, line):
        """Adds colors to individual traffic logs lines to differentiate sent vs received."""
        if ">>>" in line:
            return f"{self.G}{line}{self.X}"
        elif "<<<" in line:
            return f"{self.M}{line}{self.X}"
        elif "[SYSTEM]" in line:
            return f"{self.C}{line}{self.X}"
        return line

    def extract_doc_section(self, full_path, section_name):
        """Extracts a section from a markdown file starting with a heading matching section_name."""
        if not os.path.isfile(full_path):
            return None
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return None
            
        start_idx = -1
        heading_level = 0
        for idx, line in enumerate(lines):
            if section_name.lower() in line.lower() and line.strip().startswith("#"):
                start_idx = idx
                heading_level = len(line) - len(line.lstrip('#'))
                break
                
        if start_idx == -1:
            return None
            
        extracted = []
        for idx in range(start_idx, len(lines)):
            line = lines[idx]
            if idx > start_idx:
                if line.strip().startswith("#"):
                    current_level = len(line) - len(line.lstrip('#'))
                    if current_level <= heading_level:
                        break
            extracted.append(line)
            
        return "".join(extracted).strip()

    def print_doc_info(self, doc_file, doc_sections, indent_str="      "):
        """Prints documentation link and extracted markdown sections to console."""
        if not doc_file:
            return
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, ".."))
        full_path = os.path.join(project_root, doc_file)
        
        link = f"file://{full_path}"
        print(f"{indent_str}{self.B}Documentation :{self.X} {doc_file} ({link})")
        
        for section in doc_sections:
            content = self.extract_doc_section(full_path, section)
            if content:
                print(f"\n{indent_str}{self.BO}─── EXTRAIT DE LA DOC : {section} ────────────────────{self.X}")
                for line in content.split("\n"):
                    print(f"{indent_str}  {line}")

    def print_test_metadata(self, tc, indent_str="      "):
        """DRY printer for standard test case information (expected behavior, concept, guidance, doc links)."""
        print(f"{indent_str}{self.B}Attendu :{self.X} {tc.expected_behavior}")
        print(f"{indent_str}{self.Y}Concept :{self.X} {tc.concept}")
        print(f"{indent_str}{self.Y}Guidance:{self.X} {tc.guidance}")
        if tc.doc_file:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, ".."))
            full_path = os.path.join(project_root, tc.doc_file)
            link = f"file://{full_path}"
            print(f"{indent_str}{self.B}Doc     :{self.X} {tc.doc_file} ({link})")

    def print_run_start(self, tc):
        """Prints the starting message of a test (only in full verbose mode)."""
        if self.verbose == 3:
            print(f"  {self.sym_run}  {self.B}[ RUN  ]{self.X} {tc.name}...")

    def print_test_success(self, tc):
        """Renders test success details based on verbosity levels."""
        if self.verbose == 0:
            print(f"  {self.sym_pass}  {self.G}[ PASS ]{self.X} {tc.name}")
        elif self.verbose == 1:
            print(f"  {self.sym_pass}  {self.G}[ PASS ]{self.X} {tc.name}\n      {self.B}→ OK: {tc.expected_behavior}{self.X}")
        elif self.verbose == 3:
            print(f"  {self.sym_pass}  {self.G}[ PASS ]{self.X} {self.BO}{tc.name}{self.X}")
            self.print_test_metadata(tc, indent_str="      ")
            print()

    def print_test_failure(self, tc, err_msg, tb_str, tracked_clients):
        """Renders test failure details including logs, tracebacks, and documentation excerpts."""
        if self.verbose == 0:
            print(f"  {self.sym_fail}  {self.R}[ FAIL ]{self.X} {tc.name} - {self.R}Failed: {err_msg}{self.X}")
        elif self.verbose == 1:
            print(f"  {self.sym_fail}  {self.R}[ FAIL ]{self.X} {self.BO}{tc.name}{self.X}")
            print(f"      {self.R}Erreur   :{self.X} {err_msg}")
            self.print_test_metadata(tc, indent_str="      ")
            self.print_doc_info(tc.doc_file, tc.doc_sections, indent_str="      ")
        elif self.verbose == 3:
            print(f"  {self.sym_fail}  {self.R}[ FAIL ]{self.X} {self.BO}{tc.name}{self.X}")
            print(f"      {self.R}Erreur   :{self.X} {err_msg}")
            
            print(f"\n      {self.BO}─── TRACEBACK ──────────────────────────────────────────{self.X}")
            indented_tb = "\n".join("        " + line for line in tb_str.strip().split("\n"))
            print(indented_tb)
            
            print(f"\n      {self.BO}─── COMPORTEMENT ATTENDU ───────────────────────────────{self.X}")
            print(f"        {tc.expected_behavior}")
            
            print(f"\n      {self.BO}─── CONCEPT & GUIDANCE ─────────────────────────────────{self.X}")
            self.print_test_metadata(tc, indent_str="        ")
            self.print_doc_info(tc.doc_file, tc.doc_sections, indent_str="        ")
            
            has_traffic = any(len(c.history) > 0 for c in tracked_clients)
            if has_traffic:
                print(f"\n      {self.BO}─── TRAFIC DES CLIENTS DE CE TEST ──────────────────────{self.X}")
                for cli in tracked_clients:
                    if len(cli.history) > 0:
                        print(f"        {self.B}Client '{cli.nick}':{self.X}")
                        traffic_lines = cli.get_traffic_log().split("\n")
                        for line in traffic_lines:
                            print(f"          {self.format_traffic_line(line)}")
            print(f"      {self.BO}────────────────────────────────────────────────────────{self.X}\n")

    def print_summary(self, passed, failed):
        """Displays a stylized execution summary card with a progress bar."""
        total = passed + failed
        passed_pct = (passed / total * 100) if total > 0 else 0
        
        # Build progress bar
        filled_width = int(self.bar_width * (passed_pct / 100))
        bar = "█" * filled_width + "░" * (self.bar_width - filled_width)
        
        bar_color = self.G if failed == 0 else self.Y
        
        # summary box drawing
        w = self.summary_width
        border_top = "╔" + "═" * w + "╗"
        border_mid = "╠" + "═" * w + "╣"
        border_bot = "╚" + "═" * w + "╝"
        
        title = "BILAN DE L'EXÉCUTION"
        title_padding = (w - len(title)) // 2
        title_line = "║" + " " * title_padding + title + " " * (w - len(title) - title_padding) + "║"
        
        lbl_total = f"  Total Tests : {total}"
        lbl_total_line = "║" + lbl_total + " " * (w - len(lbl_total)) + "║"
        
        # Success and Failure require careful len computation due to ANSI escapes
        # Format the numbers, then pad
        passed_text = f"{passed} ({passed_pct:.1f}%)"
        passed_label = f"  Réussis     : {self.G}{passed_text}{self.X}"
        passed_len = len("  Réussis     : ") + len(passed_text)
        passed_line = "║" + passed_label + " " * (w - passed_len) + "║"
        
        fail_color = self.R if failed > 0 else ""
        fail_text = f"{failed}"
        fail_label = f"  Échoués     : {fail_color}{fail_text}{self.X}"
        fail_len = len("  Échoués     : ") + len(fail_text)
        fail_line = "║" + fail_label + " " * (w - fail_len) + "║"
        
        # Progress bar
        bar_label = f"  Progression : {bar_color}{bar}{self.X}"
        bar_len = len("  Progression : ") + self.bar_width
        bar_line = "║" + bar_label + " " * (w - bar_len) + "║"
        
        print(f"\n{self.BO}{border_top}")
        print(title_line)
        print(border_mid)
        print(lbl_total_line)
        print(passed_line)
        print(fail_line)
        print(bar_line)
        print(f"{border_bot}{self.X}\n")

    def print_error(self, message):
        """Displays standard premium error message."""
        print(f"  {self.BO}{self.R}ERREUR : {message}{self.X}")
