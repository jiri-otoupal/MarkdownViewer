#!/usr/bin/env python3
"""
Uninstaller for Markdown Viewer.
Removes files, shortcuts, and registry entries.
"""

import os
import sys
import shutil
import winreg
from pathlib import Path

def remove_files():
    """Remove installed files."""
    print("🗑️  Removing files...")
    
    install_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "MarkdownViewer"
    
    if install_dir.exists():
        try:
            shutil.rmtree(install_dir)
            print(f"✅ Removed {install_dir}")
            return True
        except PermissionError:
            print(f"❌ Permission denied removing {install_dir}")
            print("Please run as administrator")
            return False
        except Exception as e:
            print(f"❌ Error removing files: {e}")
            return False
    else:
        print("✅ Installation directory not found (already removed)")
        return True

def remove_shortcuts():
    """Remove Start Menu and desktop shortcuts."""
    print("🔗 Removing shortcuts...")
    
    try:
        # Start Menu
        start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Markdown Viewer"
        if start_menu.exists():
            shutil.rmtree(start_menu)
            print(f"✅ Removed Start Menu folder: {start_menu}")
        
        # Desktop shortcuts
        desktop = Path.home() / "Desktop"
        for shortcut_name in ["Markdown Viewer.lnk", "Markdown Viewer.bat"]:
            shortcut_path = desktop / shortcut_name
            if shortcut_path.exists():
                shortcut_path.unlink()
                print(f"✅ Removed desktop shortcut: {shortcut_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error removing shortcuts: {e}")
        return False

def remove_file_associations():
    """Remove file associations."""
    print("📄 Removing file associations...")
    
    try:
        # Remove extensions
        extensions = [".md", ".markdown", ".mdown"]
        
        for ext in extensions:
            try:
                # Remove from OpenWithList
                try:
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{ext}\\OpenWithList\\MarkdownViewer.exe")
                except FileNotFoundError:
                    pass
                
                # Check if extension points to our document type
                try:
                    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                        value, _ = winreg.QueryValueEx(key, "")
                        if value == "MarkdownViewer.Document":
                            winreg.DeleteValue(key, "")
                            print(f"✅ Removed association for {ext}")
                except (FileNotFoundError, OSError):
                    pass
                
            except Exception as e:
                print(f"⚠️  Could not remove association for {ext}: {e}")
        
        # Remove document type
        try:
            winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, "MarkdownViewer.Document")
            print("✅ Removed document type")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️  Could not remove document type: {e}")
        
        # Remove application registration
        try:
            winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, "Applications\\MarkdownViewer.exe")
            print("✅ Removed application registration")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️  Could not remove application registration: {e}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error removing file associations: {e}")
        return False

def remove_from_path():
    """Remove from PATH environment variable."""
    print("🛤️  Removing from PATH...")
    
    try:
        install_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "MarkdownViewer"
        install_path_str = str(install_dir)
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
                
                # Remove from PATH
                path_parts = current_path.split(";")
                new_parts = [part for part in path_parts if part != install_path_str]
                
                if len(new_parts) != len(path_parts):
                    new_path = ";".join(new_parts)
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    print(f"✅ Removed {install_path_str} from PATH")
                else:
                    print("✅ Not found in PATH")
                
            except FileNotFoundError:
                print("✅ PATH variable not found")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error removing from PATH: {e}")
        return False

def main():
    """Main uninstallation process."""
    print("🗑️  Markdown Viewer - Uninstaller")
    print("=" * 40)
    
    # Confirm uninstallation
    try:
        response = input("Are you sure you want to uninstall Markdown Viewer? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Uninstallation cancelled")
            return False
    except KeyboardInterrupt:
        print("\n❌ Uninstallation cancelled")
        return False
    
    print()
    
    # Remove shortcuts first (doesn't require admin)
    remove_shortcuts()
    
    # Remove from PATH
    remove_from_path()
    
    # Remove file associations (requires admin)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    if is_admin:
        remove_file_associations()
    else:
        print("⚠️  Skipping file associations removal (requires administrator)")
    
    # Remove files (requires admin for Program Files)
    remove_files()
    
    print()
    print("🎉 Uninstallation completed!")
    print("Thank you for using Markdown Viewer")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Uninstallation cancelled")
        sys.exit(1)
