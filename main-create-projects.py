#!/usr/bin/env python3
from WebsiteTester import WebsiteTester, SUPABASE_KEY, SESSION
from supabaseclient import SupabaseClient

"""
Website Testing Script - Username/Password Authentication
For testing: https://electr0alpha.netlify.app/conversionnet/login
"""

def main():
    """Main interactive testing interface"""
    tester = WebsiteTester()
    tester.login()
    S = SupabaseClient(tester.config)
    S.create_project()

if __name__ == '__main__':
    main()
    