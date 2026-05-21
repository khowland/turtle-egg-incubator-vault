import sys

# Read the file
with open('/a0/helpers/api.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'def requires_auth(f):' in line:
        new_lines.append(line)
        new_lines.append('    @wraps(f)\n')
        new_lines.append('    async def decorated(*args, **kwargs):\n')
        new_lines.append('        from helpers import login\n')
        new_lines.append('        from helpers.network import is_loopback_address\n')
        new_lines.append('        # Internal bypass for bot bridge\n')
        new_lines.append('        if is_loopback_address(str(request.remote_addr)) or str(request.remote_addr).startswith("172."):\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        user_pass_hash = login.get_credentials_hash()\n')
        new_lines.append('        if not user_pass_hash:\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        if session.get("authentication") != user_pass_hash:\n')
        new_lines.append('            return redirect(url_for("login_handler"))\n')
        new_lines.append('        return await f(*args, **kwargs)\n')
        skip = True
        continue
    
    if skip:
        if line.strip() == 'return decorated':
            new_lines.append('\n')
            new_lines.append(line)
            skip = False
        continue
    
    new_lines.append(line)

with open('/a0/helpers/api.py', 'w') as f:
    f.writelines(new_lines)
