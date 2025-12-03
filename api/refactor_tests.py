#!/usr/bin/env python3
"""Refactor test_create_booking.py to use booking_request() builder."""

import re
from pathlib import Path


def extract_field_value(json_dict: str, field: str) -> str | None:
    """Extract value for a specific field from JSON dict string."""
    # Pattern: "field": value (handles strings, vars, and .isoformat() calls)
    pattern = rf'"{field}":\s*(.+?)(?:,|\n|\}})'
    match = re.search(pattern, json_dict)
    if match:
        value = match.group(1).strip()
        # Remove .isoformat() if present
        value = re.sub(r'\.isoformat\(\)', '', value)
        # Remove quotes for string literals
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value
    return None


def convert_to_booking_request(json_dict: str) -> str:
    """Convert JSON dict to booking_request() call."""
    # Extract all field values
    first_name = extract_field_value(json_dict, "requester_first_name")
    email = extract_field_value(json_dict, "requester_email")
    start_date = extract_field_value(json_dict, "start_date")
    end_date = extract_field_value(json_dict, "end_date")
    party_size = extract_field_value(json_dict, "party_size")
    affiliation = extract_field_value(json_dict, "affiliation")
    description = extract_field_value(json_dict, "description")
    long_stay = extract_field_value(json_dict, "long_stay_confirmed")

    # Build booking_request() call with only non-default values
    params = []

    # Check for non-default values (defaults: Test, test@example.com, today+10/14, 4, Ingeborg, None, False)
    if first_name and first_name not in ['"Test"']:
        params.append(f"requester_first_name={first_name}")

    if email and email not in ['"test@example.com"']:
        params.append(f"requester_email={email}")

    # For dates, include if they're variables or specific literals
    if start_date and start_date != '"today + timedelta(days=10)"':
        params.append(f"start_date={start_date}")

    if end_date and end_date != '"today + timedelta(days=14)"':
        params.append(f"end_date={end_date}")

    if party_size and party_size != "4":
        params.append(f"party_size={party_size}")

    if affiliation and affiliation not in ['"Ingeborg"']:
        params.append(f"affiliation={affiliation}")

    if description and description != "None":
        params.append(f"description={description}")

    if long_stay and long_stay != "False":
        params.append(f"long_stay_confirmed={long_stay}")

    # Format the call
    if len(params) == 0:
        return "json=booking_request()"
    elif len(params) <= 2:
        return f"json=booking_request({', '.join(params)})"
    else:
        # Multi-line for readability
        param_str = ',\n            '.join(params)
        return f"json=booking_request(\n            {param_str},\n        )"


def refactor_file(file_path: Path) -> tuple[str, int]:
    """Refactor test file to use booking_request(). Returns (new_content, num_replacements)."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Pattern to match JSON dicts in client.post()
    # This matches the entire json={...} block
    pattern = r'json=\{[^{]*?"requester_first_name":[^}]*?"requester_email":[^}]*?(?:"start_date"|"party_size"):[^}]*?\}'

    def replacer(match):
        json_dict = match.group(0)
        return convert_to_booking_request(json_dict)

    new_content, num_replacements = re.subn(pattern, replacer, content, flags=re.DOTALL)

    return new_content, num_replacements


if __name__ == '__main__':
    file_path = Path('tests/integration/test_create_booking.py')

    print(f"Refactoring {file_path}...")
    new_content, num_replacements = refactor_file(file_path)

    print(f"Made {num_replacements} replacements")

    # Show before/after line count
    old_lines = len(open(file_path).readlines())
    new_lines = len(new_content.splitlines())
    reduction = old_lines - new_lines
    percent = (reduction / old_lines) * 100 if old_lines > 0 else 0

    print(f"Lines: {old_lines} → {new_lines} ({reduction} lines removed, {percent:.1f}% reduction)")

    # Write back
    with open(file_path, 'w') as f:
        f.write(new_content)

    print("✓ File refactored successfully")
