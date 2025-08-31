#!/usr/bin/env python3
"""
Simple installer script for Markdown Viewer.
Takes the built exe and installs it properly on Windows.
"""

import os
import sys
import shutil
import winreg
from pathlib import Path

def check_admin():
    """Check if running as administrator."""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

def install_files():
    """Copy files to installation directory."""
    print("📁 Installing files...")
    
    # Installation directory
    install_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "MarkdownViewer"
    
    # Check if exe exists
    exe_source = Path("dist/MarkdownViewer.exe")
    if not exe_source.exists():
        print("❌ MarkdownViewer.exe not found in dist/ folder")
        print("Please build the executable first")
        return None
    
    try:
        # Create installation directory
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        exe_dest = install_dir / "MarkdownViewer.exe"
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Copied executable to {exe_dest}")
        
        # Copy icon if exists
        icon_source = Path("src/resources/icon.ico")
        if icon_source.exists():
            resources_dir = install_dir / "resources"
            resources_dir.mkdir(exist_ok=True)
            icon_dest = resources_dir / "icon.ico"
            shutil.copy2(icon_source, icon_dest)
            print(f"✅ Copied icon to {icon_dest}")
        
        # Copy sample file if exists
        sample_source = Path("sample.md")
        if sample_source.exists():
            sample_dest = install_dir / "sample.md"
            shutil.copy2(sample_source, sample_dest)
            print(f"✅ Copied sample to {sample_dest}")
        
        return install_dir
        
    except PermissionError:
        print("❌ Permission denied. Please run as administrator.")
        return None
    except Exception as e:
        print(f"❌ Error installing files: {e}")
        return None

def create_start_menu_shortcuts(install_dir):
    """Create Start Menu shortcuts."""
    print("🔗 Creating Start Menu shortcuts...")
    
    try:
        # Start Menu Programs folder
        start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        app_folder = start_menu / "Markdown Viewer"
        app_folder.mkdir(exist_ok=True)
        
        # Try to create shortcuts using win32com
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Main application shortcut
            shortcut_path = app_folder / "Markdown Viewer.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(install_dir / "MarkdownViewer.exe")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = str(install_dir / "resources" / "icon.ico")
            shortcut.Description = "Modern Markdown editor and viewer"
            shortcut.save()
            print(f"✅ Created shortcut: {shortcut_path}")
            
            # Sample file shortcut
            if (install_dir / "sample.md").exists():
                sample_shortcut_path = app_folder / "Sample Document.lnk"
                sample_shortcut = shell.CreateShortCut(str(sample_shortcut_path))
                sample_shortcut.Targetpath = str(install_dir / "sample.md")
                sample_shortcut.WorkingDirectory = str(install_dir)
                sample_shortcut.IconLocation = str(install_dir / "resources" / "icon.ico")
                sample_shortcut.Description = "Sample Markdown document"
                sample_shortcut.save()
                print(f"✅ Created sample shortcut: {sample_shortcut_path}")
            
        except ImportError:
            print("⚠️  pywin32 not available, creating simple shortcuts")
            # Create simple batch files as shortcuts
            batch_path = app_folder / "Markdown Viewer.bat"
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\nstart "" "{install_dir / "MarkdownViewer.exe"}"\n')
            print(f"✅ Created batch shortcut: {batch_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not create Start Menu shortcuts: {e}")
        return False

def create_desktop_shortcut(install_dir):
    """Create desktop shortcut."""
    print("🖥️  Creating desktop shortcut...")
    
    try:
        desktop = Path.home() / "Desktop"
        
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            
            shortcut_path = desktop / "Markdown Viewer.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(install_dir / "MarkdownViewer.exe")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = str(install_dir / "resources" / "icon.ico")
            shortcut.Description = "Modern Markdown editor and viewer"
            shortcut.save()
            print(f"✅ Created desktop shortcut: {shortcut_path}")
            
        except ImportError:
            # Create batch file
            batch_path = desktop / "Markdown Viewer.bat"
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\nstart "" "{install_dir / "MarkdownViewer.exe"}"\n')
            print(f"✅ Created desktop batch: {batch_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")
        return False

def register_file_associations(install_dir):
    """Register file associations for Markdown files."""
    print("📄 Registering file associations...")
    
    try:
        exe_path = str(install_dir / "MarkdownViewer.exe")
        icon_path = str(install_dir / "resources" / "icon.ico")
        
        # Extensions to associate
        extensions = [".md", ".markdown", ".mdown"]
        
        for ext in extensions:
            try:
                # Create/open extension key
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext) as ext_key:
                    winreg.SetValue(ext_key, "", winreg.REG_SZ, "MarkdownViewer.Document")
                
                # Add to OpenWithList
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{ext}\\OpenWithList\\MarkdownViewer.exe") as open_key:
                    pass  # Just create the key
                
                print(f"✅ Associated {ext} files")
                
            except Exception as e:
                print(f"⚠️  Could not associate {ext}: {e}")
        
        # Register document type
        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "MarkdownViewer.Document") as doc_key:
                winreg.SetValue(doc_key, "", winreg.REG_SZ, "Markdown Document")
                
                # Set default icon
                with winreg.CreateKey(doc_key, "DefaultIcon") as icon_key:
                    winreg.SetValue(icon_key, "", winreg.REG_SZ, icon_path)
                
                # Set open command
                with winreg.CreateKey(doc_key, "shell\\open\\command") as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            print("✅ Registered document type")
            
        except Exception as e:
            print(f"⚠️  Could not register document type: {e}")
        
        # Register application
        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "Applications\\MarkdownViewer.exe") as app_key:
                winreg.SetValue(app_key, "", winreg.REG_SZ, "Markdown Viewer")
                
                # Set icon
                with winreg.CreateKey(app_key, "DefaultIcon") as icon_key:
                    winreg.SetValue(icon_key, "", winreg.REG_SZ, icon_path)
                
                # Set command
                with winreg.CreateKey(app_key, "shell\\open\\command") as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
                
                # Set supported types
                with winreg.CreateKey(app_key, "SupportedTypes") as types_key:
                    for ext in extensions + [".txt"]:
                        winreg.SetValue(types_key, ext, winreg.REG_SZ, "")
            
            print("✅ Registered application")
            
        except Exception as e:
            print(f"⚠️  Could not register application: {e}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not register file associations: {e}")
        return False

def add_to_path(install_dir):
    """Add installation directory to PATH (optional)."""
    print("🛤️  Adding to PATH...")
    
    try:
        # Get current PATH
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            install_path_str = str(install_dir)
            
            # Check if already in PATH
            if install_path_str not in current_path:
                new_path = f"{current_path};{install_path_str}" if current_path else install_path_str
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"✅ Added {install_path_str} to PATH")
                
                # Notify system of environment change
                try:
                    import win32gui
                    import win32con
                    win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, "Environment")
                except ImportError:
                    print("⚠️  Please restart your command prompt to use 'MarkdownViewer' command")
            else:
                print("✅ Already in PATH")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not add to PATH: {e}")
        return False

def main():
    """Main installation process."""
    print("🎯 Markdown Viewer - Simple Installer")
    print("=" * 40)
    
    # Check if running as admin
    if not check_admin():
        print("⚠️  Not running as administrator")
        print("Some features (file associations) may not work properly")
        print("Consider running as administrator for full installation")
        print()
    
    # Install files
    install_dir = install_files()
    if not install_dir:
        print("❌ Installation failed")
        return False
    
    print(f"📁 Installation directory: {install_dir}")
    
    # Create shortcuts
    create_start_menu_shortcuts(install_dir)
    
    # Ask about desktop shortcut
    try:
        response = input("Create desktop shortcut? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            create_desktop_shortcut(install_dir)
    except KeyboardInterrupt:
        print()
    
    # Register file associations (requires admin)
    if check_admin():
        register_file_associations(install_dir)
        
        # Ask about PATH
        try:
            response = input("Add to PATH environment variable? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                add_to_path(install_dir)
        except KeyboardInterrupt:
            print()
    else:
        print("⚠️  Skipping file associations (requires administrator)")
    
    print()
    print("🎉 Installation completed!")
    print(f"📁 Installed to: {install_dir}")
    print("🔍 Check Start Menu for 'Markdown Viewer'")
    
    # Ask to launch
    try:
        response = input("Launch Markdown Viewer now? (Y/n): ").strip().lower()
        if response not in ['n', 'no']:
            os.startfile(str(install_dir / "MarkdownViewer.exe"))
    except KeyboardInterrupt:
        print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
