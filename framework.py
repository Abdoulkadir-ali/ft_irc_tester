import sys
import traceback
import os
from irc_client import IRCClient
from printer import IRCPrinter

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

class TestRunner:
    def __init__(self, server_manager, printer=None):
        self.server_manager = server_manager
        self.printer = printer or IRCPrinter()
        self.passed = 0
        self.failed = 0

    def run_all(self):
        current_phase = None
        self.server_manager.start()
        
        try:
            for tc in all_test_cases:
                if tc.phase != current_phase:
                    current_phase = tc.phase
                    self.printer.print_section(current_phase)
                
                self.run_single_test(tc)
        finally:
            self.server_manager.stop()
            
        self.printer.print_summary(self.passed, self.failed)
        return self.failed == 0

    def run_single_test(self, tc):
        tracked_clients = []
        
        def create_client(nick):
            cli = IRCClient(nick, self.server_manager.host, self.server_manager.port)
            tracked_clients.append(cli)
            return cli

        self.printer.print_run_start(tc)

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

        # Delegated printing to print helper
        if success:
            self.printer.print_test_success(tc)
        else:
            self.printer.print_test_failure(tc, err_msg, tb_str, tracked_clients)



