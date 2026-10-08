import logging
import sys
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class CustomFormatter(logging.Formatter):
    format_str = "%(asctime)s | %(levelname)s | %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.CYAN + format_str + Style.RESET_ALL,
        logging.INFO: Fore.WHITE + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + format_str + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name="AgentLogger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate logs if instantiated multiple times
    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
        
    return logger

agent_logger = setup_logger()

def log_event(event_type: str, step: str = "", tool: str = "", status: str = "", latency: int = 0, error: str = "", attempt: int = 1):
    msg = f"{event_type}"
    if step: msg += f" | {step}"
    if tool: msg += f" | {tool}"
    if status: msg += f" | {status}"
    if latency: msg += f" | {latency}ms"
    if attempt > 1: msg += f" | attempt:{attempt}"
    if error: msg += f" | error: {error}"
    
    if status == "FAILED" or "FAILURE" in event_type or error:
        agent_logger.error(msg)
    elif status == "SUCCESS" or "SUCCESS" in event_type:
        agent_logger.info(Fore.GREEN + msg)
    else:
        agent_logger.info(msg)
