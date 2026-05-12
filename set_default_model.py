import os
path = "/a0/.env"
if os.path.exists(path):
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        found = False
        for line in lines:
            if line.startswith("CHAT_MODEL="):
                f.write("CHAT_MODEL=gemini-3.1-pro\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write("CHAT_MODEL=gemini-3.1-pro\n")
    print("CHAT_MODEL upgraded to gemini-3.1-pro")
else:
    print(".env not found")
