#!/usr/bin/env python3
"""
Deploy Real Estate CRM to DigitalOcean App Platform
Task 7-8: Complete DigitalOcean CI/CD Setup
"""
import requests
import json
import os

# DigitalOcean Configuration
DO_TOKEN = os.environ.get('DIGITALOCEAN_TOKEN', 'your-do-token-here')
GITHUB_REPO = "endersclarity/ai-enhanced-real-estate-crm"
BRANCH = "feature/cloud-deployment"

def create_digitalocean_app():
    """Create DigitalOcean App Platform deployment"""
    
    app_config = {
        "spec": {
            "name": "real-estate-crm-prod",
            "region": "nyc",
            "services": [
            {
                "name": "web",
                "source_dir": "/",
                "github": {
                    "repo": GITHUB_REPO,
                    "branch": BRANCH,
                    "deploy_on_push": True
                },
                "run_command": "python app.py",
                "environment_slug": "python",
                "instance_count": 1,
                "instance_size_slug": "basic-xxs",
                "http_port": 8080,
                "envs": [
                    {
                        "key": "USE_SUPABASE",
                        "value": "true",
                        "scope": "RUN_TIME"
                    },
                    {
                        "key": "SUPABASE_URL",
                        "value": "https://pfcdqrxnjyarhueofrsn.supabase.co",
                        "scope": "RUN_TIME"
                    },
                    {
                        "key": "SUPABASE_ANON_KEY",
                        "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmY2Rxcnhuanlhcmh1ZW9mcnNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MTUyMzEsImV4cCI6MjA2NDM5MTIzMX0.04ZvxzZn43utA1SNnqTvhjquhI801gNDcH-rJTMbIzA",
                        "scope": "RUN_TIME"
                    },
                    {
                        "key": "GEMINI_API_KEY",
                        "value": "AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU",
                        "scope": "RUN_TIME"
                    },
                    {
                        "key": "FLASK_ENV",
                        "value": "production",
                        "scope": "RUN_TIME"
                    }
                ]
            }
        ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {DO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Creating DigitalOcean App Platform deployment...")
    print(f"   Repository: {GITHUB_REPO}")
    print(f"   Branch: {BRANCH}")
    print(f"   Auto-deploy: Enabled")
    
    response = requests.post(
        "https://api.digitalocean.com/v2/apps",
        headers=headers,
        json=app_config
    )
    
    if response.status_code == 201:
        app_data = response.json()
        app_id = app_data['app']['id']
        app_url = app_data['app'].get('live_url', 'URL will be available after deployment')
        
        print(f"✅ App created successfully!")
        print(f"   App ID: {app_id}")
        print(f"   Live URL: {app_url}")
        print(f"   Dashboard: https://cloud.digitalocean.com/apps/{app_id}")
        
        # Wait for deployment
        print("\n⏳ Deployment in progress...")
        print("   This may take 5-10 minutes for the first deployment")
        print("   Once complete, your app will auto-deploy on every git push!")
        
        return app_id, app_url
    else:
        print(f"❌ Failed to create app: {response.status_code}")
        print(f"   Error: {response.text}")
        return None, None

def check_app_status(app_id):
    """Check deployment status"""
    headers = {
        "Authorization": f"Bearer {DO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://api.digitalocean.com/v2/apps/{app_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        app_data = response.json()
        app = app_data['app']
        
        print(f"\n📊 App Status: {app.get('phase', 'Unknown')}")
        print(f"   Live URL: {app.get('live_url', 'Not yet available')}")
        
        # Check deployments
        deployments = app.get('last_deployment_created_at', 'No deployments')
        print(f"   Last deployment: {deployments}")
        
        return app.get('live_url')
    else:
        print(f"❌ Failed to check status: {response.status_code}")
        return None

if __name__ == "__main__":
    print("🏠 Real Estate CRM - DigitalOcean Deployment Setup")
    print("=================================================")
    
    # Check if app already exists
    headers = {"Authorization": f"Bearer {DO_TOKEN}"}
    response = requests.get("https://api.digitalocean.com/v2/apps", headers=headers)
    
    existing_app = None
    if response.status_code == 200:
        apps = response.json().get('apps', [])
        for app in apps:
            if app['spec']['name'] == 'real-estate-crm-prod':
                existing_app = app
                break
    
    if existing_app:
        app_id = existing_app['id']
        print(f"✅ Found existing app: {app_id}")
        live_url = check_app_status(app_id)
        if live_url:
            print(f"\n🌐 Your live app URL: {live_url}")
            print("   Changes pushed to GitHub will auto-deploy!")
    else:
        app_id, live_url = create_digitalocean_app()
        if app_id:
            print(f"\n🎉 Setup complete! Your CI/CD pipeline is ready.")
            print(f"   Every git push to '{BRANCH}' will trigger automatic deployment.")