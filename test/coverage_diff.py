#!/usr/bin/env python3

import argparse
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class CoverageEntry:
    """Represents a function's coverage information"""
    file_path: str
    line_info: str  # Line number or block info
    function_name: str
    coverage_percent: float

    @classmethod
    def parse_from_line(cls, line: str) -> Optional['CoverageEntry']:
        """Parse a line from a coverage report file"""
        try:
            # Split by tabs or multiple spaces
            parts = re.split(r'\s{2,}|\t+', line.strip())

            if len(parts) < 2 or not parts[-1].endswith('%'):
                return None

            coverage_str = parts[-1].strip()
            coverage_percent = float(coverage_str.rstrip('%'))

            function_name = parts[-2].strip()

            file_line_parts = parts[0].strip().rsplit(':', 1)
            if len(file_line_parts) < 2:
                return None

            file_path = file_line_parts[0]
            line_info = file_line_parts[1].rstrip(':')

            return cls(
                file_path=file_path,
                line_info=line_info,
                function_name=function_name,
                coverage_percent=coverage_percent
            )
        except (ValueError, IndexError):
            return None


def load_coverage_file(file_path: str) -> Tuple[Dict[str, CoverageEntry], Optional[float]]:
    """Load a coverage file and return a dictionary of coverage entries and total coverage"""
    coverage_dict = {}
    total_coverage = None

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('total:'):
                    parts = re.split(r'\s{2,}|\t+', line)
                    if parts[-1].endswith('%'):
                        total_coverage = float(parts[-1].rstrip('%'))
                    continue

                entry = CoverageEntry.parse_from_line(line)
                if entry:
                    # Use file_path:function_name as the key
                    key = f"{entry.file_path}:{entry.function_name}"
                    coverage_dict[key] = entry

        return coverage_dict, total_coverage

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)


def compare_coverage(before_file: str, after_file: str) -> None:
    """Compare coverage between two files and print the diff"""
    before_coverage, before_total = load_coverage_file(before_file)
    after_coverage, after_total = load_coverage_file(after_file)

    # Get all unique keys
    all_keys = set(before_coverage.keys()) | set(after_coverage.keys())

    # Print total coverage change
    if before_total is not None and after_total is not None:
        diff = after_total - before_total
        diff_str = f"{diff:+.1f}%" if diff != 0 else "no change"
        color = ""
        reset = ""
        if diff > 0:
            color = "\033[32m"  # Green
            reset = "\033[0m"
        elif diff < 0:
            color = "\033[31m"  # Red
            reset = "\033[0m"

        print(f"Total Coverage: {before_total:.1f}% → {after_total:.1f}% ({color}{diff_str}{reset})")
        print()

    # Create lists for different types of changes
    changed = []
    new = []
    removed = []

    # Categorize changes
    for key in all_keys:
        before_entry = before_coverage.get(key)
        after_entry = after_coverage.get(key)

        if before_entry and after_entry:
            if before_entry.coverage_percent != after_entry.coverage_percent:
                changed.append((key, before_entry, after_entry))
        elif after_entry and not before_entry:
            new.append((key, after_entry))
        elif before_entry and not after_entry:
            removed.append((key, before_entry))

    # Sort changed functions by magnitude of change
    changed.sort(key=lambda x: abs(x[2].coverage_percent - x[1].coverage_percent), reverse=True)

    # Print changed functions
    if changed:
        print(f"FUNCTIONS WITH CHANGED COVERAGE ({len(changed)} total):")
        print(f"{'FUNCTION'.ljust(110)} | {'BEFORE'.rjust(6)} | {'AFTER'.rjust(6)} | CHANGE")
        print(f"{'-' * 110}-+-{'-' * 6}-+-{'-' * 6}-+-------")

        for key, before_entry, after_entry in changed:
            before_pct = before_entry.coverage_percent
            after_pct = after_entry.coverage_percent
            diff = after_pct - before_pct

            # Format the difference with color
            if diff > 0:
                diff_str = f"\033[32m+{diff:.1f}%\033[0m"
            else:
                diff_str = f"\033[31m{diff:.1f}%\033[0m"

            # Format function name with file
            func_display = f"{before_entry.file_path}:{before_entry.function_name}"
            if len(func_display) > 109:
                # Truncate with ellipsis if too long
                func_display = "..." + func_display[-106:]

            print(f"{func_display.ljust(110)} | {before_pct:6.1f}% | {after_pct:6.1f}% | {diff_str}")
    else:
        print("No functions with changed coverage")

    # Print new functions
    if new:
        print(f"\nNEW FUNCTIONS ({len(new)} total):")
        print(f"{'FUNCTION'.ljust(110)} | COVERAGE")
        print(f"{'-' * 110}-+--------")

        for key, entry in sorted(new, key=lambda x: x[1].file_path):
            # Format function name with file
            func_display = f"{entry.file_path}:{entry.function_name}"
            if len(func_display) > 109:
                # Truncate with ellipsis if too long
                func_display = "..." + func_display[-106:]

            print(f"{func_display.ljust(110)} | {entry.coverage_percent:6.1f}%")

    # Print removed functions
    if removed:
        print(f"\nREMOVED FUNCTIONS ({len(removed)} total):")
        print(f"{'FUNCTION'.ljust(110)} | COVERAGE")
        print(f"{'-' * 110}-+--------")

        for key, entry in sorted(removed, key=lambda x: x[1].file_path):
            # Format function name with file
            func_display = f"{entry.file_path}:{entry.function_name}"
            if len(func_display) > 109:
                # Truncate with ellipsis if too long
                func_display = "..." + func_display[-106:]

            print(f"{func_display.ljust(110)} | {entry.coverage_percent:6.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description='Compare two Go coverage report files and show function-level differences',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'before_file',
        help='First (before) coverage report file'
    )

    parser.add_argument(
        'after_file',
        help='Second (after) coverage report file'
    )

    args = parser.parse_args()

    try:
        compare_coverage(args.before_file, args.after_file)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
