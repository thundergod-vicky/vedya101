#!/usr/bin/env python3
"""
VEDYA Deployment Helper
Automates deployment to different platforms
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def deploy_backend_railway():
    """Deploy backend to Railway."""
    print("\n🚂 Deploying Backend to Railway...")
    
    # Check if Railway CLI is installed
    if not run_command("railway --version", "Checking Railway CLI"):
        print("❌ Railway CLI not found. Install with: npm install -g @railway/cli")
        return False
    
    # Deploy to Railway
    commands = [
        ("railway login", "Railway login (follow browser prompt)"),
        ("railway up", "Deploying to Railway")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print("✅ Backend deployed to Railway!")
    return True

def deploy_frontend_vercel():
    """Deploy frontend to Vercel."""
    print("\n▲ Deploying Frontend to Vercel...")
    
    # Change to frontend directory
    os.chdir("frontend")
    
    # Check if Vercel CLI is installed
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("❌ Vercel CLI not found. Install with: npm install -g vercel")
        return False
    
    # Build and deploy to Vercel
    commands = [
        ("npm run build", "Building production frontend"),
        ("vercel --prod", "Deploying to Vercel")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    # Return to root directory
    os.chdir("..")
    
    print("✅ Frontend deployed to Vercel!")
    return True

def main():
    """Main deployment orchestrator."""
    print("🎯 VEDYA Deployment Helper")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python deploy.py backend     # Deploy only backend to Railway")
        print("  python deploy.py frontend    # Deploy only frontend to Vercel")
        print("  python deploy.py full        # Deploy both backend and frontend")
        print("  python deploy.py check       # Check deployment requirements")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        print("🔍 Checking deployment requirements...")
        
        # Check CLI tools
        tools = [
            ("node --version", "Node.js"),
            ("npm --version", "npm"),
            ("python --version", "Python"),
            ("git --version", "Git")
        ]
        
        for tool_command, tool_name in tools:
            if run_command(tool_command, f"Checking {tool_name}"):
                pass
            else:
                print(f"❌ {tool_name} not found")
        
        # Check if in correct directory
        if not Path("frontend").exists() or not Path("api_server.py").exists():
            print("❌ Run this script from the VEDYA root directory")
            return
        
        print("✅ All requirements check passed!")
    
    elif command == "backend":
        deploy_backend_railway()
    
    elif command == "frontend":
        deploy_frontend_vercel()
    
    elif command == "full":
        print("🚀 Full deployment starting...")
        if deploy_backend_railway() and deploy_frontend_vercel():
            print("\n🎉 Full deployment completed successfully!")
            print("\n📋 Next steps:")
            print("1. Update frontend environment variables in Vercel dashboard")
            print("2. Set NEXT_PUBLIC_API_URL to your Railway backend URL")
            print("3. Test the deployed application")
        else:
            print("\n❌ Deployment failed. Check the errors above.")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python deploy.py' without arguments to see usage.")

if __name__ == "__main__":
    main()
