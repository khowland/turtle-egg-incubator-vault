#!/usr/bin/env python3
"""
CR-20260430-194500 Phase 0.2: Archive outdated migration scripts.

Moves specified migration files from supabase_db/migrations/ to supabase_db/archive/.
Duplicate handling: if a file with the same name already exists in archive,
rename to <filename>.dup before moving; skip if that .dup also exists.
Skips files that don't exist at source.
"""

import os
import shutil

BASE_DIR = '/a0/usr/workdir'
MIGRATIONS_DIR = os.path.join(BASE_DIR, 'supabase_db', 'migrations')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'supabase_db', 'archive')

# Files to archive
TARGET_FILES = [
    'RPC_VAULT_FINALIZE_INTAKE.sql',
    'v8_1_16_ADD_TEMP_TO_BIN_OBS.sql',
    'v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql',
    'v8_1_19_ENFORCE_TIMESTAMP_SOVEREIGNTY.sql',
    'v8_1_21_ADD_DAYS_IN_CARE.sql',
    'v8_1_22_MOTHER_WEIGHT.sql',
    'v8_1_25_SUPPLEMENTAL_INTAKE.sql',
    'v8_1_27_RPC_VAULT_ADMIN_RESTORE_V2.sql',
]

def main():
    moved = []
    skipped = []
    errors = []

    # Ensure archive directory exists
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    for fname in TARGET_FILES:
        src = os.path.join(MIGRATIONS_DIR, fname)
        dest = os.path.join(ARCHIVE_DIR, fname)

        if not os.path.isfile(src):
            msg = f"Source not found, skipped: {src}"
            print(msg)
            skipped.append((fname, 'source missing'))
            continue

        # Handle duplicate at destination
        if os.path.exists(dest):
            # Try .dup suffix
            alt_fname = fname + '.dup'
            alt_dest = os.path.join(ARCHIVE_DIR, alt_fname)
            if os.path.exists(alt_dest):
                msg = f"Both {fname} and {alt_fname} exist in archive, skipping."
                print(msg)
                skipped.append((fname, 'duplicate at destination'))
                continue
            # Move with .dup name
            try:
                shutil.move(src, alt_dest)
                print(f"Moved {src} -> {alt_dest} (as .dup)")
                moved.append((fname, alt_fname))
            except Exception as e:
                print(f"Error moving {src} to {alt_dest}: {e}")
                errors.append((fname, str(e)))
        else:
            try:
                shutil.move(src, dest)
                print(f"Moved {src} -> {dest}")
                moved.append((fname, fname))
            except Exception as e:
                print(f"Error moving {src} to {dest}: {e}")
                errors.append((fname, str(e)))

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Moved: {len(moved)}")
    for orig, final in moved:
        print(f"  {orig} -> {final}")
    print(f"Skipped: {len(skipped)}")
    for name, reason in skipped:
        print(f"  {name}: {reason}")
    print(f"Errors: {len(errors)}")
    for name, err in errors:
        print(f"  {name}: {err}")

    if errors:
        sys.exit(1)

if __name__ == '__main__':
    import sys
    main()
