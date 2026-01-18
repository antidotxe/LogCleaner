import os
import sys
import logging
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

ASCII_TAG = r"""
                         ,--,                
,-.----.              ,---.'|                
\    /  \    ,----..  |   | :     ,----..    
|   :    \  /   /   \ :   : |    /   /   \   
|   |  .\ :|   :     :|   ' :   |   :     :  
.   :  |: |.   |  ;. /;   ; '   .   |  ;. /  
|   |   \ :.   ; /--` '   | |__ .   ; /--`   
|   : .   /;   | ;    |   | :.'|;   | ;  __  
;   | |`-' |   : |    '   :    ;|   : |.' .' 
|   | ;    .   | '___ |   |  ./ .   | '_.' : 
:   ' |    '   ; : .'|;   : ;   '   ; : \  | 
:   : :    '   | '/  :|   ,/    '   | '/  .' 
|   | :    |   :    / '---'     |   :    /   
`---'.|     \   \ .'             \   \ .'    
  `---`      `---`                `---`      
"""

MENU = """
Log Cleaner
===========
1) Remove duplicates
2) Reformat to Email:Pass
3) Remove whitespaces
4) Run all (1-3)
5) Exit
"""

RED = "\x1b[31m"
RESET = "\x1b[0m"

LOG_DIR = "logs"


def setup_logging(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(base_dir, f"logcleaner_{ts}.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return log_path


def pick_input_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(title="Select input file")
    root.destroy()
    return file_path


def pick_output_dir():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    dir_path = filedialog.askdirectory(title="Select output directory")
    root.destroy()
    return dir_path


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def remove_duplicates(lines):
    seen = set()
    out = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def remove_whitespace(lines):
    email_pass_re = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}:.+$")
    out = []
    for line in lines:
        compact = "".join(line.split())
        if not compact:
            continue
        if email_pass_re.match(compact):
            out.append(compact)
    return out


def reformat_email_pass(lines):
    sep_chars = [":", "|", ";", ",", " ", "\t"]
    email_re = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    out = []
    i = 0
    while i < len(lines):
        raw = lines[i].strip()
        if not raw:
            i += 1
            continue
            # ik this is very messy with a bunch of fuck ass cases but i cba to make this clean :sob:
        match = re.search(email_re, raw)
        if match:
            user = match.group(0)
            password = ""

            
            after = raw[match.end() :]
            for sep in sep_chars:
                after = after.replace(sep, ":")
            parts_after = [p for p in after.split(":") if p != ""]
            if parts_after:
                password = parts_after[0]

            if not password and i + 1 < len(lines):
                next_raw = lines[i + 1].strip()
                if next_raw:
                    temp = next_raw
                    for sep in sep_chars:
                        temp = temp.replace(sep, ":")
                    parts_next = [p for p in temp.split(":") if p != ""]
                    if parts_next:
                        if parts_next[0].lower() == "pass" and len(parts_next) >= 2:
                            password = parts_next[1]
                        elif parts_next[0].lower() in ("password", "pwd") and len(parts_next) >= 2:
                            password = parts_next[1]
                        else:
                            password = parts_next[0]
                if password:
                    i += 1 

            if user and password:
                out.append(f"{user}:{password}")
            i += 1
            continue

        normalized = raw
        for sep in sep_chars:
            normalized = normalized.replace(sep, ":")
        parts = [p for p in normalized.split(":") if p != ""]
        if len(parts) >= 2:
            email_part = next((p for p in parts if re.search(email_re, p)), "")
            if email_part:
                pass_part = next((p for p in parts if p != email_part), "")
                if pass_part:
                    out.append(f"{email_part}:{pass_part}")
                    i += 1
                    continue
            out.append(f"{parts[0]}:{parts[1]}")
        i += 1

    return out


def apply_actions(lines, actions):
    if "dedupe" in actions:
        lines = remove_duplicates(lines)
    if "reformat" in actions:
        lines = reformat_email_pass(lines)
    if "whitespace" in actions:
        lines = remove_whitespace(lines)
    return lines


def main():
    try:
        log_path = setup_logging(LOG_DIR)
        logging.info("Started")
        print(f"{RED}{ASCII_TAG}{MENU}")
        choice = input("Select option: ").strip()
        if choice == "5":
            print("Bye")
            return

        actions = set()
        if choice == "1":
            actions.add("dedupe")
        elif choice == "2":
            actions.add("reformat")
        elif choice == "3":
            actions.add("whitespace")
        elif choice == "4":
            actions.update(["dedupe", "reformat", "whitespace"])
        else:
            print("Invalid choice")
            return

        print("Select input log file...")
        input_path = pick_input_file()
        if not input_path:
            print("No input selected")
            return
        output_dir = pick_output_dir()
        if not output_dir:
            print("No output directory selected")
            return

        lines = read_lines(input_path)
        logging.info("Read %d lines from %s", len(lines), input_path)
        out_lines = apply_actions(lines, actions)
        logging.info("Output %d lines after processing", len(out_lines))

        base = os.path.splitext(os.path.basename(input_path))[0]
        out_name = f"{base}_cleaned.txt"
        out_path = os.path.join(output_dir, out_name)
        write_lines(out_path, out_lines)

        print(f"Saved: {out_path}")
        print(f"Log: {log_path}")
        logging.info("Saved output to %s", out_path)
    except Exception as e:
        logging.exception("Unhandled error")
        print(f"Error: {e}")
    finally:
        print(RESET, end="")


if __name__ == "__main__":
    main()
