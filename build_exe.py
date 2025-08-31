#!/usr/bin/env python3
"""
Build script for creating a standalone executable using Nuitka.
"""

import subprocess
import sys
from pathlib import Path
import shutil

def check_nuitka():
    """Check if Nuitka is installed."""
    try:
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Nuitka found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Nuitka not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Nuitka: {e}")
        return False

def install_nuitka():
    """Install Nuitka if not present."""
    print("📦 Installing Nuitka...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"], check=True)
        print("✅ Nuitka installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Nuitka: {e}")
        return False

def build_executable():
    """Build the standalone executable with Nuitka."""
    print("🔨 Building standalone executable with Nuitka...")
    
    # Ensure icon exists
    icon_path = Path("src/resources/icon.ico")
    if not icon_path.exists():
        print("⚠️  Icon file not found, building without icon")
        icon_arg = []
    else:
        icon_arg = [f"--windows-icon-from-ico={icon_path}"]
    
    # Nuitka command arguments
    nuitka_args = [
        sys.executable, "-m", "nuitka",
        
        # Basic options
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        
        # Include packages explicitly (without plugin to avoid pkg_resources issue)
        "--include-package=PySide6",
        "--include-package=markdown",
        "--include-package=pygments",
        "--include-package=bleach",
        "--include-package=src",
        "--nofollow-import-to=unittest",
        # Include data files
        "--include-data-dir=src/resources=src/resources",
        
        # Windows specific
        "--windows-console-mode=disable",
        "--assume-yes-for-downloads",
        
        # Output options
        "--output-filename=MarkdownViewer.exe",
        "--output-dir=dist",
        
        # Optimization (reduced for compatibility)
        "--jobs=6",
        
        # Main file
        "main.py"
    ]
    
    # Add icon if available
    if icon_arg:
        nuitka_args.extend(icon_arg)
    
    print("🚀 Running Nuitka compilation...")
    print(f"Command: {' '.join(nuitka_args)}")
    
    try:
        # Run Nuitka
        result = subprocess.run(nuitka_args, check=True)
        
        print("✅ Compilation successful!")
        
        # Check if executable was created
        exe_path = Path("dist/MarkdownViewer.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📁 Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Copy sample file to dist
            sample_path = Path("sample.md")
            if sample_path.exists():
                shutil.copy2(sample_path, "dist/sample.md")
                print("📄 Copied sample.md to dist/")
            
            return True
        else:
            print("❌ Executable not found after compilation")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main build process."""
    print("🎯 Markdown Viewer - Nuitka Build Script")
    print("=" * 50)
    
    # Check if Nuitka is installed
    if not check_nuitka():
        if not install_nuitka():
            print("❌ Cannot proceed without Nuitka")
            return False
    
    # Create dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(exist_ok=True)
    
    # Build executable
    success = build_executable()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("📁 Executable location: dist/MarkdownViewer.exe")
        print("🚀 You can now distribute the standalone executable")
    else:
        print("\n❌ Build failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
