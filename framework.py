import sys
import traceback
import os
from irc_client import IRCClient

# Colors
G = "\033[92m"  # Green
R = "\033[91m"  # Red
Y = "\033[93m"  # Yellow
B = "\033[94m"  # Blue
BO = "\033[1m" # Bold
X = "\033[0m"  # Reset

class TestCase:
    def __init__(self, name, phase, expected_behavior, concept, guidance, run_fn, doc_file=None, doc_sections=None):
        self.name = name
        self.phase = phase
        self.expected_behavior = expected_behavior
        self.concept = concept
        self.guidance = guidance
        self.run_fn = run_fn
        self.doc_file = doc_file
        self.doc_sections = doc_sections or []

all_test_cases = []

def test_case(phase, name, expected_behavior, concept, guidance, doc_file=None, doc_sections=None):
    """Decorator to register a test case."""
    def decorator(run_fn):
        tc = TestCase(name, phase, expected_behavior, concept, guidance, run_fn, doc_file, doc_sections)
        all_test_cases.append(tc)
        return run_fn
    return decorator

def extract_doc_section(full_path, section_name):
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

def print_doc_info(doc_file, doc_sections, indent_str="      "):
    """Prints documentation link and extracted markdown sections to console."""
    if not doc_file:
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    full_path = os.path.join(project_root, doc_file)
    
    link = f"file://{full_path}"
    print(f"{indent_str}{B}Documentation :{X} {doc_file} ({link})")
    
    for section in doc_sections:
        content = extract_doc_section(full_path, section)
        if content:
            print(f"\n{indent_str}{BO}─── EXTRAIT DE LA DOC : {section} ────────────────────{X}")
            for line in content.split("\n"):
                print(f"{indent_str}  {line}")

class TestRunner:
    def __init__(self, server_manager, verbose=0):
        self.server_manager = server_manager
        self.verbose = verbose  # 0: False, 1: True, 3: Full
        self.passed = 0
        self.failed = 0

    def run_all(self):
        current_phase = None
        self.server_manager.start()
        
        try:
            for tc in all_test_cases:
                if tc.phase != current_phase:
                    current_phase = tc.phase
                    self.print_section(current_phase)
                
                self.run_single_test(tc)
        finally:
            self.server_manager.stop()
            
        self.print_summary()
        return self.failed == 0

    def print_section(self, phase_name):
        print(f"\n{BO}{'─'*60}\n  {phase_name}\n{'─'*60}{X}")

    def run_single_test(self, tc):
        tracked_clients = []
        
        def create_client(nick):
            cli = IRCClient(nick, self.server_manager.host, self.server_manager.port)
            tracked_clients.append(cli)
            return cli

        if self.verbose == 3:
            print(f"  {B}Running:{X} {tc.name}...")

        success = False
        err_msg = ""
        tb_str = ""

        try:
            tc.run_fn(create_client, self.server_manager.password)
            success = True
            self.passed += 1
        except Exception as e:
            self.failed += 1
            err_msg = f"{type(e).__name__}: {str(e)}"
            tb_str = traceback.format_exc()
        finally:
            for cli in tracked_clients:
                try:
                    cli.close()
                except Exception:
                    pass

        # Print output depending on verbosity and success
        if success:
            if self.verbose == 0:
                print(f"  {G}✓{X} {tc.name}")
            elif self.verbose == 1:
                print(f"  {G}✓{X} {tc.name}\n    {B}→ OK: {tc.expected_behavior}{X}")
            elif self.verbose == 3:
                print(f"  {G}✓{X} {tc.name} - PASSED")
                print(f"    {B}Attendu :{X} {tc.expected_behavior}")
                print(f"    {Y}Concept :{X} {tc.concept}")
                print(f"    {Y}Guidance:{X} {tc.guidance}")
                if tc.doc_file:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.abspath(os.path.join(script_dir, ".."))
                    full_path = os.path.join(project_root, tc.doc_file)
                    link = f"file://{full_path}"
                    print(f"    {B}Documentation :{X} {tc.doc_file} ({link})")
                print()
        else:
            if self.verbose == 0:
                print(f"  {R}✗{X} {tc.name} - {R}Failed: {err_msg}{X}")
            elif self.verbose == 1:
                print(f"  {R}✗{X} {tc.name}")
                print(f"    {R}Erreur   :{X} {err_msg}")
                print(f"    {Y}Attendu  :{X} {tc.expected_behavior}")
                print(f"    {Y}Concept  :{X} {tc.concept}")
                print(f"    {Y}Guidance :{X} {tc.guidance}")
                print_doc_info(tc.doc_file, tc.doc_sections, indent_str="    ")
            elif self.verbose == 3:
                print(f"  {R}✗{X} {tc.name} - {R}FAILED{X}")
                print(f"    {R}Erreur   :{X} {err_msg}")
                
                print(f"\n    {BO}─── TRACEBACK ──────────────────────────────────────────{X}")
                indented_tb = "\n".join("      " + line for line in tb_str.strip().split("\n"))
                print(indented_tb)
                
                print(f"\n    {BO}─── COMPORTEMENT ATTENDU ───────────────────────────────{X}")
                print(f"      {tc.expected_behavior}")
                
                print(f"\n    {BO}─── CONCEPT & GUIDANCE ─────────────────────────────────{X}")
                print(f"      {Y}Notion  :{X} {tc.concept}")
                print(f"      {Y}Guidance:{X} {tc.guidance}")
                print_doc_info(tc.doc_file, tc.doc_sections, indent_str="      ")
                
                has_traffic = any(len(c.history) > 0 for c in tracked_clients)
                if has_traffic:
                    print(f"\n    {BO}─── TRAFIC DES CLIENTS DE CE TEST ──────────────────────{X}")
                    for cli in tracked_clients:
                        if len(cli.history) > 0:
                            print(f"      {B}Client '{cli.nick}':{X}")
                            traffic_lines = cli.get_traffic_log().split("\n")
                            for line in traffic_lines:
                                print(f"        {line}")
                print(f"    {BO}────────────────────────────────────────────────────────{X}\n")

    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'═'*60}")
        print(f"{BO}  {G}{self.passed}{X}{BO} réussis / {R}{self.failed}{X}{BO} échoués / {total} total{X}")
        print(f"{'═'*60}\n")

