#!/usr/bin/env python3
"""
Script to update CRAN download counts from live data
Run this script when you have internet access to get real download counts

Usage:
    python3 update_cran_counts.py

This script will:
1. Fetch real download counts from CRAN APIs
2. Update the index.html file with current counts
3. Show before/after comparison
"""

import requests
import json
import re
import os
from datetime import datetime

# The packages we track
PACKAGES = ['DeclareDesign', 'estimatr', 'fabricatr', 'list', 'rr']

def get_cran_downloads(package_name):
    """
    Get total download counts from CRAN logs API
    Tries multiple endpoints for best coverage
    """
    
    # Try cranlogs.r-pkg.org first (most comprehensive)
    try:
        url = f"https://cranlogs.r-pkg.org/downloads/total/{package_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'downloads' in data and data['downloads'] > 0:
            print(f"✓ {package_name}: {data['downloads']:,} total downloads (cranlogs)")
            return data['downloads']
            
    except requests.RequestException as e:
        print(f"  cranlogs API failed for {package_name}: {e}")
    
    # Try METACRAN API as backup
    try:
        url = f"https://api.r-hub.io/packages/{package_name}/downloads"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'count' in data and data['count'] > 0:
            print(f"✓ {package_name}: {data['count']:,} total downloads (METACRAN)")
            return data['count']
            
    except requests.RequestException as e:
        print(f"  METACRAN API failed for {package_name}: {e}")
    
    print(f"✗ Could not fetch data for {package_name}")
    return None

def format_download_count(count):
    """Format download count in thousands (K) for display"""
    if count is None:
        return None
    
    if count >= 1000:
        k_count = round(count / 1000)
        return f"{k_count:,},000"
    else:
        return str(count)

def update_html_counts(html_file_path, new_counts):
    """Update the download counts in the HTML file"""
    
    if not os.path.exists(html_file_path):
        print(f"Error: File {html_file_path} not found")
        return False
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Regex patterns for each package
    patterns = {
        'DeclareDesign': r'(&ldquo;<b>DeclareDesign</b>:.*?~)(\d+,?\d*)(.*downloads\.)',
        'estimatr': r'(&ldquo;<b>estimatr</b>:.*?~)(\d+,?\d*)(.*downloads\.)',
        'fabricatr': r'(&ldquo;<b>fabricatr</b>:.*?~)(\d+,?\d*)(.*downloads\.)',
        'list': r'(&ldquo;<b>list</b>:.*?~)(\d+,?\d*)(.*downloads\.)',
        'rr': r'(&ldquo;<b>rr</b>:.*?~)(\d+,?\d*)(.*downloads\.)',
    }
    
    updates_made = {}
    
    for package, pattern in patterns.items():
        if package in new_counts and new_counts[package] is not None:
            formatted_count = format_download_count(new_counts[package])
            
            # Find and replace the pattern
            match = re.search(pattern, content, re.DOTALL)
            if match:
                old_count = match.group(2)
                new_text = match.group(1) + formatted_count + match.group(3)
                content = re.sub(pattern, new_text, content, flags=re.DOTALL)
                updates_made[package] = {
                    'old': old_count,
                    'new': formatted_count,
                    'actual_count': new_counts[package]
                }
                print(f"Updated {package}: {old_count} -> {formatted_count}")
            else:
                print(f"Warning: Could not find pattern for {package}")
    
    # Write the updated content back to the file
    if content != original_content and updates_made:
        # Create backup
        backup_file = html_file_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup created: {backup_file}")
        
        # Write updated file
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nSuccessfully updated {len(updates_made)} download counts in {html_file_path}")
        return True
    else:
        print("No changes were made to the file")
        return False

def main():
    """Main function"""
    print("Fetching real CRAN download counts...")
    print("=" * 60)
    
    # Fetch download counts
    download_counts = {}
    
    for package in PACKAGES:
        print(f"\nFetching data for {package}...")
        count = get_cran_downloads(package)
        download_counts[package] = count
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COUNT SUMMARY:")
    print("=" * 60)
    
    total_downloads = 0
    successful_fetches = 0
    
    for package in PACKAGES:
        count = download_counts[package]
        if count is not None:
            print(f"{package:15}: {count:,} downloads")
            total_downloads += count
            successful_fetches += 1
        else:
            print(f"{package:15}: Data not available")
    
    if successful_fetches > 0:
        print(f"\nTotal downloads: {total_downloads:,}")
        print(f"Successfully fetched {successful_fetches}/{len(PACKAGES)} package counts")
        
        # Update the HTML file
        html_file = "index.html"
        if os.path.exists(html_file):
            print(f"\nUpdating {html_file}...")
            success = update_html_counts(html_file, download_counts)
            
            if success:
                print("\n✓ Download counts updated successfully!")
                print(f"✓ Backup created for safety")
                print(f"✓ Total downloads across packages: {total_downloads:,}")
            else:
                print("\n✗ Failed to update HTML file")
        else:
            print(f"\n✗ HTML file '{html_file}' not found in current directory")
    else:
        print("\n✗ Could not fetch any download counts")
        print("This might be due to:")
        print("  - Network connectivity issues")
        print("  - CRAN API temporarily unavailable")
        print("  - Package names changed or removed")

if __name__ == "__main__":
    main()