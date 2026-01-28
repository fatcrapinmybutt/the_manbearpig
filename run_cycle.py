#!/usr/bin/env python3
"""
CLI wrapper for Convergence Cycle Engine
=========================================

Provides easy command-line access to the convergence cycle system.

Usage:
    python run_cycle.py              # Run a full convergence cycle
    python run_cycle.py --status     # Check current version status
    python run_cycle.py --history    # Show version history
    python run_cycle.py --snapshot   # Create snapshot without full cycle
"""

import argparse
import json
import sys
from pathlib import Path

from convergence_cycle_engine import ConvergenceCycleEngine


def show_status():
    """Show current version status."""
    version_file = Path("VERSION")
    current_file = Path("CURRENT")
    manifest_file = Path("codex_manifest.json")
    
    print("\n" + "=" * 60)
    print("CONVERGENCE CYCLE STATUS")
    print("=" * 60)
    
    if version_file.exists():
        version = version_file.read_text().strip()
        print(f"Current Version: {version}")
    else:
        print("Current Version: Not initialized")
    
    if current_file.exists():
        current = current_file.read_text().strip()
        print(f"Runnable Version: {current}")
    else:
        print("Runnable Version: Not set")
    
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        print(f"Modules Tracked: {len(manifest)}")
    else:
        print("Modules Tracked: 0")
    
    versions_dir = Path("VERSIONS")
    if versions_dir.exists():
        snapshots = list(versions_dir.iterdir())
        print(f"Version Snapshots: {len(snapshots)}")
    else:
        print("Version Snapshots: 0")
    
    output_dir = Path("output")
    if output_dir.exists():
        releases = list(output_dir.glob("*.zip"))
        print(f"Release Packages: {len(releases)}")
    else:
        print("Release Packages: 0")
    
    print("=" * 60 + "\n")


def show_history():
    """Show version history from CHANGELOG."""
    changelog_file = Path("CHANGELOG.md")
    
    if not changelog_file.exists():
        print("No CHANGELOG found.")
        return
    
    print("\n" + "=" * 60)
    print("VERSION HISTORY")
    print("=" * 60)
    
    content = changelog_file.read_text()
    lines = content.split("\n")
    
    version_count = 0
    for line in lines:
        if line.startswith("## [v"):
            print(line[3:])
            version_count += 1
            if version_count >= 10:
                print("\n... (see CHANGELOG.md for full history)")
                break
    
    print("=" * 60 + "\n")


def create_snapshot():
    """Create a snapshot without running full cycle."""
    engine = ConvergenceCycleEngine()
    current_version = engine.read_version()
    engine.current_version = current_version
    
    print(f"\nCreating snapshot for {current_version}...")
    snapshot_dir = engine.snapshot_version()
    print(f"✓ Snapshot created: {snapshot_dir}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convergence Cycle Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_cycle.py                  # Run full convergence cycle
  python run_cycle.py --status         # Show current status
  python run_cycle.py --history        # Show version history
  python run_cycle.py --snapshot       # Create snapshot only
        """
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current version status"
    )
    
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show version history"
    )
    
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Create snapshot without running full cycle"
    )
    
    args = parser.parse_args()
    
    # Handle commands
    if args.status:
        show_status()
    elif args.history:
        show_history()
    elif args.snapshot:
        create_snapshot()
    else:
        # Run full convergence cycle
        print("\n" + "=" * 60)
        print("RUNNING CONVERGENCE CYCLE")
        print("=" * 60 + "\n")
        
        engine = ConvergenceCycleEngine()
        success = engine.run_cycle()
        
        if success:
            print("\n✓ Convergence cycle completed successfully!")
            show_status()
            sys.exit(0)
        else:
            print("\n✗ Convergence cycle completed with failures.")
            print("  Check logs/convergence_cycle.log for details.\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
