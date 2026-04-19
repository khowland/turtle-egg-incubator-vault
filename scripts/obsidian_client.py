#!/usr/bin/env python3
"""
=============================================================================
Module:     scripts/obsidian_client.py
Project:    Turtle-DB / Obsidian Integration
Purpose:    Python client for interacting with the Obsidian Local REST API.
            Supports note CRUD, search, and dot-connecting (RAG context).
Author:     Antigravity (Automated Implementation)
Created:    2026-04-18
=============================================================================
"""
import os
import argparse
import httpx
import json
from dotenv import load_dotenv

# Load workspace environment
load_dotenv()

class ObsidianClient:
    """Client for Obsidian Local REST API."""
    
    def __init__(self, host="localhost", port=None, api_key=None, use_https=True):
        self.port = port or os.getenv("OBSIDIAN_API_PORT", "27124")
        self.api_key = api_key or os.getenv("OBSIDIAN_API_KEY")
        self.protocol = "https" if use_https else "http"
        self.base_url = f"{self.protocol}://{host}:{self.port}"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ping(self):
        """Check if the Obsidian API is reachable."""
        try:
            with httpx.Client(verify=False, timeout=5.0) as client:
                response = client.get(f"{self.base_url}/", headers=self.headers)
                if response.status_code == 200:
                    print(f"✅ Obsidian API connected on port {self.port}")
                    return True
                else:
                    print(f"❌ Failed to connect: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def list_files(self):
        """List files in the vault."""
        with httpx.Client(verify=False) as client:
            response = client.get(f"{self.base_url}/vault/", headers=self.headers)
            return response.json() if response.status_code == 200 else None

    def read_file(self, path):
        """Read a file's content from the vault."""
        with httpx.Client(verify=False) as client:
            response = client.get(f"{self.base_url}/vault/{path}", headers=self.headers)
            return response.text if response.status_code == 200 else None

    def write_file(self, path, content):
        """Write content to a file in the vault."""
        with httpx.Client(verify=False) as client:
            response = client.put(f"{self.base_url}/vault/{path}", headers=self.headers, content=content)
            return response.status_code in [200, 204]

    def search(self, query):
        """Search the vault."""
        params = {"query": query}
        with httpx.Client(verify=False) as client:
            response = client.post(f"{self.base_url}/search/", headers=self.headers, json=params)
            return response.json() if response.status_code == 200 else None

def main():
    parser = argparse.ArgumentParser(description="Obsidian Local REST API Tool")
    parser.add_argument("--action", choices=["ping", "read", "write", "search"], required=True)
    parser.add_argument("--path", help="Relative path to the note (e.g., 'Folder/Note.md')")
    parser.add_argument("--content", help="Markdown content for write action")
    parser.add_argument("--query", help="Search query")
    
    args = parser.parse_args()
    client = ObsidianClient()

    if args.action == "ping":
        client.ping()
    elif args.action == "read":
        if not args.path:
            print("Error: --path required for read")
        else:
            content = client.read_file(args.path)
            print(content if content else "File not found.")
    elif args.action == "write":
        if not args.path or not args.content:
            print("Error: --path and --content required for write")
        else:
            success = client.write_file(args.path, args.content)
            print("✅ File written" if success else "❌ Write failed")
    elif args.action == "search":
        if not args.query:
            print("Error: --query required for search")
        else:
            results = client.search(args.query)
            print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
