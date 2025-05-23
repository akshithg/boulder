#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class CoverageFunction:
    """Represents a function's coverage information"""
    file_path: str
    function_name: str
    line_number: int
    coverage_percent: float

    @classmethod
    def parse_from_line(cls, line: str) -> Optional['CoverageFunction']:
        """Parse a line from a coverage report file"""
        try:
            parts = line.strip().split()
            if len(parts) < 2 or not parts[-1].endswith('%'):
                return None

            coverage_str = parts[-1]
            function_name = parts[-2]
            file_parts = parts[0].split(':')
            file_path = file_parts[0]
            line_number = int(file_parts[1])
            coverage_percent = float(coverage_str.rstrip('%'))

            return cls(
                file_path=file_path,
                function_name=function_name,
                line_number=line_number,
                coverage_percent=coverage_percent
            )
        except (ValueError, IndexError):
            return None


class CoverageFile:
    """Represents a file's aggregate coverage information"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[CoverageFunction] = []

    def add_function(self, function: CoverageFunction) -> None:
        """Add a function's coverage data to this file"""
        self.functions.append(function)

    @property
    def coverage_percent(self) -> float:
        """Calculate the average coverage percentage for this file"""
        if not self.functions:
            return 0.0
        total = sum(func.coverage_percent for func in self.functions)
        return total / len(self.functions)

    @property
    def is_zero_coverage(self) -> bool:
        """Check if all functions in this file have 0% coverage"""
        if not self.functions:
            return True
        return all(func.coverage_percent == 0.0 for func in self.functions)


class CoverageReport:
    """Represents a full coverage report"""
    def __init__(self):
        self.functions: List[CoverageFunction] = []
        self.files: Dict[str, CoverageFile] = {}
        self.total_coverage: float = 0.0

    def parse_report_file(self, file_path: str) -> None:
        """Parse a coverage report file"""
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('total:'):
                    # Extract total coverage
                    parts = line.strip().split()
                    if parts[-1].endswith('%'):
                        self.total_coverage = float(parts[-1].rstrip('%'))
                    continue

                function = CoverageFunction.parse_from_line(line)
                if function:
                    self.functions.append(function)

                    # Add to file aggregation
                    if function.file_path not in self.files:
                        self.files[function.file_path] = CoverageFile(function.file_path)
                    self.files[function.file_path].add_function(function)

    def get_zero_coverage_files(self) -> List[str]:
        """Get a list of files with zero coverage"""
        return [file_path for file_path, file_obj in self.files.items()
                if file_obj.is_zero_coverage]


class CoverageAnalyzer:
    """Analyzes Go coverage data"""
    def __init__(self, coverage_dir: str, clean: bool = False, verbose: bool = False):
        self.coverage_dir = Path(coverage_dir)
        self.clean = clean
        self.verbose = verbose
        self.generated_files: List[Path] = []
        self.report = CoverageReport()

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def process_coverage(self) -> None:
        """Process coverage data in the specified directory"""
        self.log(f"Processing coverage data in {self.coverage_dir}")

        # Process runtime coverage files (covmeta.*)
        self._merge_runtime_coverage()

        # Process coverprofile files
        self._merge_coverprofiles()

        # Generate text reports
        self._generate_text_reports()

        # Generate HTML report
        self._generate_html_report()

        # Parse the combined report
        combined_report = self.coverage_dir / "combined.coverprofile.txt"
        if combined_report.exists():
            self.report.parse_report_file(combined_report)

    def _merge_runtime_coverage(self) -> None:
        """Merge runtime coverage files (covmeta.*)"""
        # Check for runtime coverage files
        covmeta_files = list(self.coverage_dir.glob("covmeta.*"))
        if not covmeta_files:
            self.log("No runtime coverage files found")
            return

        self.log("Found runtime coverage files, merging...")
        merged_dir = self.coverage_dir / "merged"
        merged_dir.mkdir(exist_ok=True)
        self.generated_files.append(merged_dir)

        try:
            # Merge coverage data
            subprocess.run(
                ["go", "tool", "covdata", "merge",
                 "-i", str(self.coverage_dir),
                 "-o", str(merged_dir)],
                check=True,
                capture_output=True
            )
            self.log("Successfully merged runtime coverage")

            # Convert to text format
            runtime_profile = self.coverage_dir / "runtime.coverprofile"
            subprocess.run(
                ["go", "tool", "covdata", "textfmt",
                 "-i", str(merged_dir),
                 "-o", str(runtime_profile)],
                check=True,
                capture_output=True
            )
            self.generated_files.append(runtime_profile)
            self.log(f"Converted to text format at {runtime_profile}")

        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to merge runtime coverage files: {e.stderr.decode()}", file=sys.stderr)

    def _merge_coverprofiles(self) -> None:
        """Merge coverprofile files"""
        # Find all coverprofile files, excluding already processed ones
        coverprofile_files = [
            f for f in self.coverage_dir.glob("*.coverprofile")
            if "combined" not in f.name and "filtered" not in f.name
        ]

        if not coverprofile_files:
            self.log("No coverprofile files found")
            return

        self.log("Found coverprofile files, merging...")

        # Check if gocovmerge is installed
        try:
            subprocess.run(["which", "gocovmerge"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Error: gocovmerge not found, please install it first", file=sys.stderr)
            print("Run: go install github.com/wadey/gocovmerge@latest", file=sys.stderr)
            sys.exit(1)

        # Combine coverprofile files
        combined_profile = self.coverage_dir / "combined.coverprofile"
        cmd = ["gocovmerge"] + [str(f) for f in coverprofile_files]

        with open(combined_profile, 'w') as f:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.PIPE)

        self.generated_files.append(combined_profile)
        self.log(f"Combined coverprofile created at {combined_profile}")

        # Create filtered profile
        filtered_profile = self.coverage_dir / "filtered.combined.coverprofile"
        self._filter_profile(combined_profile, filtered_profile)
        self.generated_files.append(filtered_profile)
        self.log(f"Filtered coverprofile created at {filtered_profile}")

    def _filter_profile(self, input_file: Path, output_file: Path) -> None:
        """Filter a coverage profile to exclude test files, etc."""
        exclude_patterns = [r'/test/', r'pb\.go', r'/cmd/']
        patterns = '|'.join(exclude_patterns)

        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if not re.search(patterns, line):
                    outfile.write(line)

    def _generate_text_reports(self) -> None:
        """Generate plaintext coverage reports"""
        self.log("Generating readable coverage reports...")

        for profile in self.coverage_dir.glob("*.coverprofile"):
            # Skip text reports that might already exist
            if profile.name.endswith(".txt"):
                continue

            output_file = profile.with_suffix(profile.suffix + ".txt")

            try:
                subprocess.run(
                    ["go", "tool", "cover", "-func", str(profile)],
                    check=True,
                    stdout=open(output_file, 'w'),
                    stderr=subprocess.PIPE
                )
                self.generated_files.append(output_file)
                self.log(f"Generated text report for {profile.name}")
            except subprocess.CalledProcessError as e:
                print(f"Error generating text report for {profile}: {e.stderr.decode()}", file=sys.stderr)

    def _generate_html_report(self) -> None:
        """Generate HTML coverage report"""
        combined_profile = self.coverage_dir / "combined.coverprofile"
        if not combined_profile.exists():
            return

        self.log("Generating HTML coverage report...")
        html_output = self.coverage_dir / "coverage.html"

        try:
            subprocess.run(
                ["go", "tool", "cover", "-html", str(combined_profile), "-o", str(html_output)],
                check=True,
                stderr=subprocess.PIPE
            )
            self.generated_files.append(html_output)
            self.log(f"HTML coverage report generated at {html_output}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating HTML report: {e.stderr.decode()}", file=sys.stderr)

    def generate_summary_report(self) -> Dict:
        """Generate a summary report as a dictionary"""
        zero_coverage_files = self.report.get_zero_coverage_files()

        return {
            "total_coverage": round(self.report.total_coverage, 1),
            "zero_coverage_files": sorted(zero_coverage_files),
            "zero_coverage_count": len(zero_coverage_files),
            "total_files": len(self.report.files),
            "total_functions": len(self.report.functions)
        }

    def print_summary(self, label: str = "") -> None:
        """Print a summary of the coverage report to stdout"""
        summary = self.generate_summary_report()

        if label:
            print(f"{label} Coverage: {summary['total_coverage']}% ({summary['zero_coverage_count']} files with 0% coverage)")
        else:
            print(f"Coverage: {summary['total_coverage']}% ({summary['zero_coverage_count']} files with 0% coverage)")

    def clean_generated_files(self) -> None:
        """Clean up generated files"""
        if not self.clean:
            return

        self.log("\nCleaning up generated files...")
        for file_path in self.generated_files:
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    self.log(f"Removed directory: {file_path}")
                else:
                    file_path.unlink()
                    self.log(f"Removed file: {file_path}")

        self.log("Cleanup complete!")


class CoverageComparator:
    """Compares coverage between two directories"""
    def __init__(self, dir1: str, dir2: str, verbose: bool = False):
        self.analyzer1 = CoverageAnalyzer(dir1, verbose=verbose)
        self.analyzer2 = CoverageAnalyzer(dir2, verbose=verbose)
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def compare(self) -> Dict:
        """Process and compare coverage between the two directories"""
        # Process coverage in both directories
        self.analyzer1.process_coverage()
        self.analyzer2.process_coverage()

        # Return comparison report
        return self._generate_comparison_report()

    def _generate_comparison_report(self) -> Dict:
        """Generate a comparison report between the two directories"""
        report1 = self.analyzer1.report
        report2 = self.analyzer2.report

        # Compare total coverage
        total1 = report1.total_coverage
        total2 = report2.total_coverage
        diff = total2 - total1

        # Zero coverage files
        zero_files1 = set(report1.get_zero_coverage_files())
        zero_files2 = set(report2.get_zero_coverage_files())

        # Files that went from zero coverage to some coverage
        improved = zero_files1 - zero_files2

        # Files that went from some coverage to zero coverage
        worsened = zero_files2 - zero_files1

        # Files with zero coverage in both directories
        unchanged = zero_files1 & zero_files2

        return {
            "dir1": {
                "total_coverage": round(total1, 1),
                "zero_coverage_count": len(zero_files1),
                "total_files": len(report1.files),
                "total_functions": len(report1.functions)
            },
            "dir2": {
                "total_coverage": round(total2, 1),
                "zero_coverage_count": len(zero_files2),
                "total_files": len(report2.files),
                "total_functions": len(report2.functions)
            },
            "comparison": {
                "coverage_diff": round(diff, 1),
                "improved": sorted(list(improved)),
                "worsened": sorted(list(worsened)),
                "unchanged_zero": sorted(list(unchanged)),
                "improved_count": len(improved),
                "worsened_count": len(worsened),
                "unchanged_zero_count": len(unchanged)
            }
        }

    def print_summary(self) -> None:
        """Print a summary of the comparison to stdout"""
        report = self._generate_comparison_report()

        dir1 = report["dir1"]
        dir2 = report["dir2"]
        comparison = report["comparison"]

        print(f"Coverage Change: {dir1['total_coverage']}% → {dir2['total_coverage']}% ", end="")

        diff = comparison["coverage_diff"]
        if diff > 0:
            print(f"(\033[32m+{diff}%\033[0m)")
        elif diff < 0:
            print(f"(\033[31m{diff}%\033[0m)")
        else:
            print("(no change)")

        print(f"Zero Coverage Files: {dir1['zero_coverage_count']} → {dir2['zero_coverage_count']} ", end="")

        zero_diff = dir1['zero_coverage_count'] - dir2['zero_coverage_count']
        if zero_diff > 0:
            print(f"(\033[32m-{zero_diff}\033[0m)")
        elif zero_diff < 0:
            print(f"(\033[31m+{abs(zero_diff)}\033[0m)")
        else:
            print("(no change)")

        if comparison["improved_count"] > 0:
            print(f"Files with improved coverage: \033[32m{comparison['improved_count']}\033[0m")

        if comparison["worsened_count"] > 0:
            print(f"Files with worsened coverage: \033[31m{comparison['worsened_count']}\033[0m")

    def clean_generated_files(self) -> None:
        """Clean up generated files in both directories"""
        self.analyzer1.clean_generated_files()
        self.analyzer2.clean_generated_files()


def write_json_report(data: Dict, output_file: str) -> None:
    """Write a report to a JSON file"""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)


def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Go Coverage Analysis Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean generated files after processing'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file for detailed report (JSON format)'
    )

    parser.add_argument(
        'coverage_dir',
        help='First coverage directory'
    )

    parser.add_argument(
        'compare_dir',
        nargs='?',
        help='Second coverage directory for comparison'
    )

    args = parser.parse_args()

    if args.compare_dir:
        # Compare two directories
        comparator = CoverageComparator(args.coverage_dir, args.compare_dir, verbose=args.verbose)
        report = comparator.compare()
        comparator.print_summary()

        if args.output:
            write_json_report(report, args.output)
            print(f"Detailed report written to {args.output}")

        if args.clean:
            comparator.clean_generated_files()
    else:
        # Process a single directory
        analyzer = CoverageAnalyzer(args.coverage_dir, args.clean, verbose=args.verbose)
        analyzer.process_coverage()
        analyzer.print_summary()

        if args.output:
            report = analyzer.generate_summary_report()
            write_json_report(report, args.output)
            print(f"Detailed report written to {args.output}")

        if args.clean:
            analyzer.clean_generated_files()


if __name__ == '__main__':
    main()
