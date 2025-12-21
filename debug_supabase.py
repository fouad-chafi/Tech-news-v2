#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

def debug_supabase():
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')

    print(f"URL: {url}")
    print(f"Service key: {key[:20]}...")

    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    # Test 1: Lister les tables disponibles
    print("\n=== Test 1: Lister les tables ===")
    try:
        response = requests.get(f"{url}/rest/v1/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Essayer de récupérer les catégories
    print("\n=== Test 2: Catégories ===")
    try:
        response = requests.get(f"{url}/rest/v1/categories?select=*&limit=5", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 403:
            print("403 Forbidden - Problem with permissions")
        elif response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} categories")
            for cat in data:
                print(f"  - {cat}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Essayer avec la clé anon au lieu de service
    print("\n=== Test 3: Avec clé ANON ===")
    anon_key = os.getenv('SUPABASE_KEY')
    if anon_key:
        headers_anon = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(f"{url}/rest/v1/categories?select=*&limit=5", headers=headers_anon)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")

    # Test 4: Vérifier si on peut créer une catégorie
    print("\n=== Test 4: Créer catégorie de test ===")
    try:
        test_data = {'name': 'TEST_DEBUG'}
        response = requests.post(f"{url}/rest/v1/categories", headers=headers, json=test_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_supabase()