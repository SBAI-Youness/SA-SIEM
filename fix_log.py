with open("auth.logs", "r") as f:
    lines = f.readlines()

cleaned = []
i = 0

while i < len(lines):
    line = lines[i].rstrip("\n")

    # If line ends with "from", join it with next line
    if line.strip().endswith("from") and i + 1 < len(lines):
        next_line = lines[i + 1].strip()
        line = line + " " + next_line
        i += 1  # skip next line

    cleaned.append(line)
    i += 1

with open("clean_auth.log", "w") as f:
    for line in cleaned:
        f.write(line + "\n")

print("File cleaned successfully.")