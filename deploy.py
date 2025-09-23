#!/usr/bin/env python3
"""
Deployment helper script for the Coding Interview Revision System.
"""

import os
import subprocess
import sys


def check_git_setup():
    """Check if git is properly set up."""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git repository not initialized")
            return False
        print("✅ Git repository found")
        return True
    except FileNotFoundError:
        print("❌ Git not found. Please install git first.")
        return False


def check_required_files():
    """Check if all required files exist."""
    required_files = [
        'web_app.py',
        'core.py', 
        'problem_bank.yaml',
        'requirements.txt',
        '.streamlit/config.toml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True


def get_github_info():
    """Get GitHub repository information."""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode != 0:
            return None, None
        
        lines = result.stdout.strip().split('\n')
        if not lines or lines[0] == '':
            return None, None
        
        # Extract username and repo name from origin URL
        origin_line = lines[0]
        if 'github.com' in origin_line:
            parts = origin_line.split('/')
            if len(parts) >= 2:
                username = parts[-2].split(':')[-1]  # Handle both https and ssh
                repo_name = parts[-1].replace('.git', '').split()[0]
                return username, repo_name
        
        return None, None
    except Exception:
        return None, None


def deploy_to_streamlit():
    """Guide user through Streamlit Cloud deployment."""
    print("\n🚀 Streamlit Cloud Deployment Guide")
    print("=" * 50)
    
    # Check prerequisites
    if not check_git_setup():
        print("\n📝 Setting up git repository...")
        subprocess.run(['git', 'init'])
        print("✅ Git repository initialized")
        print("\nNext steps:")
        print("1. Add your files: git add .")
        print("2. Commit: git commit -m 'Initial commit'")
        print("3. Add remote: git remote add origin YOUR_GITHUB_URL")
        print("4. Push: git push -u origin main")
        return
    
    if not check_required_files():
        print("\n❌ Please ensure all required files exist before deploying.")
        return
    
    # Check GitHub setup
    username, repo_name = get_github_info()
    
    if not username or not repo_name:
        print("\n📝 GitHub remote not found.")
        print("Please add your GitHub remote:")
        print("git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git")
        return
    
    print(f"✅ GitHub repository: {username}/{repo_name}")
    
    # Check if changes need to be committed
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("\n📝 You have uncommitted changes.")
            print("Committing changes...")
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', 'Update for deployment'])
            print("✅ Changes committed")
        
        # Push to GitHub
        print("📤 Pushing to GitHub...")
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Code pushed to GitHub")
        else:
            print("❌ Failed to push to GitHub")
            print("Please check your git setup and try again.")
            return
            
    except Exception as e:
        print(f"❌ Error with git operations: {e}")
        return
    
    # Deployment instructions
    print("\n🎯 Ready to Deploy!")
    print("=" * 30)
    print("1. Go to: https://share.streamlit.io")
    print("2. Click 'New app'")
    print("3. Fill in:")
    print(f"   Repository: {username}/{repo_name}")
    print("   Branch: main")
    print("   Main file path: web_app.py")
    print("4. Click 'Deploy!'")
    print()
    print("Your app will be available at:")
    print(f"https://YOUR_APP_NAME-{username}.streamlit.app")
    print()
    print("📱 The app is optimized for mobile devices!")


def main():
    """Main deployment function."""
    print("🎯 Coding Interview Revision System - Deployment Helper")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Usage: python deploy.py [options]

Options:
  --help     Show this help message

This script helps you deploy your coding interview revision system
to Streamlit Cloud for mobile access.

Prerequisites:
- Git repository with GitHub remote
- All required files present
- GitHub account
- Streamlit Cloud account (sign up at share.streamlit.io)
""")
        return
    
    try:
        deploy_to_streamlit()
    except KeyboardInterrupt:
        print("\n👋 Deployment cancelled.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    main()
