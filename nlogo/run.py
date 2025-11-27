#!/usr/bin/env python3
"""
Quick start script for the Credit Insurance Simulation System.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Credit Insurance Simulation System")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

