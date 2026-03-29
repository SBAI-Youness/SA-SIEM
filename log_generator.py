import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_FILE = "auth.logs"
TOTAL_LINES = 100000  # Change this to 1000000 for a massive file

# Simulated entities
USERS = ["mac", "admin", "dev_team", "postgres", "root"]
ATTACK_IPS = ["10.0.0.55", "192.168.1.200", "172.16.0.4", "45.22.11.9"]
NORMAL_IPS = ["192.168.1.10", "192.168.1.12", "192.168.1.50", "10.0.0.5"]

# Start date for the logs
current_time = datetime(2026, 3, 1, 0, 0, 0)


def generate_log_entry(timestamp):
    # Determine the type of event based on realistic probabilities
    event_type = random.choices(
        ["cron", "sudo", "su", "sshd_success", "sshd_fail", "sshd_invalid"],
        weights=[40, 15, 5, 30, 8, 2],  # 40% cron, 30% ssh success, etc.
        k=1
    )[0]

    time_str = timestamp.strftime("%b %e %H:%M:%S")
    pid = random.randint(1000, 9999)
    port = random.randint(40000, 60000)

    user = random.choice(USERS)
    normal_ip = random.choice(NORMAL_IPS)
    attack_ip = random.choice(ATTACK_IPS)

    if event_type == "cron":
        return f"{time_str} ubuntu CRON[{pid}]: pam_unix(cron:session): session opened for user root by (uid=0)\n{time_str} ubuntu CRON[{pid}]: pam_unix(cron:session): session closed for user root"

    elif event_type == "sudo":
        return f"{time_str} ubuntu sudo:      {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/bin/bash\n{time_str} ubuntu sudo: pam_unix(sudo:session): session opened for user root by {user}(uid=1000)"

    elif event_type == "su":
        return f"{time_str} ubuntu su[{pid}]: Successful su for postgres by root\n{time_str} ubuntu su[{pid}]: pam_unix(su:session): session opened for user postgres by (uid=0)"

    elif event_type == "sshd_success":
        return f"{time_str} ubuntu sshd[{pid}]: Accepted password for {user} from {normal_ip} port {port} ssh2\n{time_str} ubuntu sshd[{pid}]: pam_unix(sshd:session): session opened for user {user} by (uid=0)"

    elif event_type == "sshd_fail":
        return f"{time_str} ubuntu sshd[{pid}]: Failed password for {user} from {attack_ip} port {port} ssh2"

    elif event_type == "sshd_invalid":
        fake_user = f"testuser{random.randint(1, 99)}"
        return f"{time_str} ubuntu sshd[{pid}]: Failed password for invalid user {fake_user} from {attack_ip} port {port} ssh2"


print(f"Generating {TOTAL_LINES} log entries. This might take a few seconds...")

with open(OUTPUT_FILE, "w") as f:
    lines_written = 0
    while lines_written < TOTAL_LINES:
        # Advance time by a random amount (between 1 second and 2 minutes)
        current_time += timedelta(seconds=random.randint(1, 120))

        log_entry = generate_log_entry(current_time)
        f.write(log_entry + "\n")

        # Some events generate two lines (like cron open/close), we count them roughly
        lines_written += len(log_entry.split('\n'))

print(f"Success! {OUTPUT_FILE} has been generated.")