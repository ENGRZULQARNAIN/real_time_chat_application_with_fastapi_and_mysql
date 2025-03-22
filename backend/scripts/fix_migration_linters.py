#!/usr/bin/env python
"""
Script to fix common linter errors in Alembic migration files.
This script automatically formats migration files to follow PEP 8 guidelines.

Usage:
    python scripts/fix_migration_linters.py [migration_file_path]

If no path is provided, the script will check all migration files in app/alembic/versions/.
"""

import os
import re
import sys
import glob
from pathlib import Path


def fix_indentation(content):
    """Fix indentation in create_table blocks."""
    # Pattern to match create_table blocks
    create_table_pattern = r'(op\.create_table\([^\)]+,\n)(\s+)sa\.Column'
    # Replace with proper indentation (8 spaces after the initial indentation)
    content = re.sub(create_table_pattern, r'\1        sa.Column', content)
    
    # Fix indentation for all continuation lines in a create_table block
    lines = content.split('\n')
    in_create_table = False
    fixed_lines = []
    
    for line in lines:
        if 'op.create_table' in line:
            in_create_table = True
            fixed_lines.append(line)
        elif in_create_table and (line.strip().startswith('sa.') or line.strip().startswith('sa,')):
            # Ensure consistent indentation
            fixed_lines.append('        ' + line.strip())
        elif in_create_table and ')' in line and not (line.strip().startswith('sa.') or line.strip().startswith('sa,')):
            in_create_table = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_line_length(content):
    """Break long lines into multiple lines."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 79 and 'server_default=sa.text' in line:
            # Split server_default parameter
            parts = line.split('server_default=')
            prefix = parts[0]
            suffix = parts[1]
            fixed_lines.append(f"{prefix}server_default=")
            fixed_lines.append(f"            {suffix}")
        elif len(line) > 79 and 'ForeignKeyConstraint' in line:
            # Split ForeignKeyConstraint into multiple lines
            parts = line.split('ForeignKeyConstraint(')
            prefix = parts[0] + 'ForeignKeyConstraint('
            constraint_parts = parts[1].split(', ')
            fixed_lines.append(f"{prefix}{constraint_parts[0]},")
            fixed_lines.append(f"            {constraint_parts[1]}")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_migration_file(file_path):
    """Fix linter issues in a migration file."""
    print(f"Processing {file_path}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Apply fixes
    content = fix_indentation(content)
    content = fix_line_length(content)
    
    # Write back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed linter issues in {file_path}")


def main():
    """Main entry point."""
    # Get the migration file path from command-line argument or use default directory
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path):
            fix_migration_file(path)
        else:
            print(f"Error: File {path} does not exist.")
            sys.exit(1)
    else:
        # Process all migration files in the versions directory
        base_dir = Path(__file__).parent.parent
        versions_dir = base_dir / 'app' / 'alembic' / 'versions'
        migration_files = glob.glob(str(versions_dir / '*.py'))
        
        if not migration_files:
            print("No migration files found.")
            sys.exit(0)
        
        for file_path in migration_files:
            fix_migration_file(file_path)
    
    print("All done!")


if __name__ == "__main__":
    main() 