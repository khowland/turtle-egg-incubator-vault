import sys

# Read the file
with open('/a0/helpers/api.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_auth = False
skip_loopback = False
skip_csrf = False

for line in lines:
    # Fix csrf_protect
    if 'def csrf_protect(f):' in line:
        new_lines.append(line)
        new_lines.append('    @wraps(f)\n')
        new_lines.append('    async def decorated(*args, **kwargs):\n')
        new_lines.append('        from helpers.network import is_loopback_address\n')
        new_lines.append('        # Trust internal container traffic - bypass CSRF\n')
        new_lines.append('        if is_loopback_address(str(request.remote_addr)) or str(request.remote_addr).startswith("172."):\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        from helpers import runtime\n')
        new_lines.append('        token = session.get("csrf_token")\n')
        new_lines.append('        header = request.headers.get("X-CSRF-Token")\n')
        new_lines.append('        cookie = request.cookies.get("csrf_token_" + runtime.get_runtime_id())\n')
        new_lines.append('        sent = header or cookie\n')
        new_lines.append('        if not token or not sent or token != sent:\n')
        new_lines.append('            return Response("CSRF token missing or invalid", 403)\n')
        new_lines.append('        return await f(*args, **kwargs)\n')
        skip_csrf = True
        continue

    # Fix requires_loopback
    if 'def requires_loopback(f):' in line:
        new_lines.append(line)
        new_lines.append('    @wraps(f)\n')
        new_lines.append('    async def decorated(*args, **kwargs):\n')
        new_lines.append('        from helpers.network import is_loopback_address\n')
        new_lines.append('        # Trust all internal container traffic\n')
        new_lines.append('        if is_loopback_address(str(request.remote_addr)) or str(request.remote_addr).startswith("172."):\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        return Response("Access denied.", 403, {})\n')
        skip_loopback = True
        continue
    
    # Fix requires_auth
    if 'def requires_auth(f):' in line:
        new_lines.append(line)
        new_lines.append('    @wraps(f)\n')
        new_lines.append('    async def decorated(*args, **kwargs):\n')
        new_lines.append('        from helpers import login\n')
        new_lines.append('        from helpers.network import is_loopback_address\n')
        new_lines.append('        # Trust all internal container traffic\n')
        new_lines.append('        if is_loopback_address(str(request.remote_addr)) or str(request.remote_addr).startswith("172."):\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        user_pass_hash = login.get_credentials_hash()\n')
        new_lines.append('        if not user_pass_hash:\n')
        new_lines.append('            return await f(*args, **kwargs)\n')
        new_lines.append('        if session.get("authentication") != user_pass_hash:\n')
        new_lines.append('            return redirect(url_for("login_handler"))\n')
        new_lines.append('        return await f(*args, **kwargs)\n')
        skip_auth = True
        continue
    
    if skip_csrf:
        if line.strip() == 'return decorated':
            new_lines.append('\n')
            new_lines.append(line)
            skip_csrf = False
        continue

    if skip_loopback:
        if line.strip() == 'return decorated':
            new_lines.append('\n')
            new_lines.append(line)
            skip_loopback = False
        continue

    if skip_auth:
        if line.strip() == 'return decorated':
            new_lines.append('\n')
            new_lines.append(line)
            skip_auth = False
        continue
    
    new_lines.append(line)

with open('/a0/helpers/api.py', 'w') as f:
    f.writelines(new_lines)
