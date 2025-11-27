#!/usr/bin/env python3
"""
Run script for the Credit Insurance Simulation System (Streamlit).
"""
import subprocess
import sys
import os

if __name__ == '__main__':
    print("=" * 60)
    print("Credit Insurance Simulation System")
    print("=" * 60)
    print("\nStarting Streamlit server...")
    print("The application will open in your default browser.")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

