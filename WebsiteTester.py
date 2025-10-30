from datetime import datetime
import json
import urllib
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import os
import dotenv

dotenv.load_dotenv()

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SESSION = {
    'supabase_url':     os.getenv('SUPABASE_URL'),
    'base_url':         os.getenv('ELECTROMOTIVE_URL'),
    'login_url':        os.getenv('ELECTROMOTIVE_LOGIN_URL'),
    'username':         os.getenv('ELCTROMOTIVE_USER'),
    'password':         os.getenv('ELCTROMOTIVE_PASSWORD'),
    'session_file':     'session_data.json', # where to write the seesion data
    'user_id':          None,   # will be filled after login
    'user_profile':     None,   # will be filled after fetching profile
}

class WebsiteTester:
    """Handles authentication and testing for the website"""
    
    def __init__(self):
        self.config = SESSION
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.authenticated = False
        self.session_data = {}

    def get_projects(self, user_id):
        url: str =  urljoin(self.config['base_url'], f'projects')
        params:str = urllib.parse.urlencode({'id': f'eq.{user_id}', 'select': '*'})
        h =  {
            "Content-Type": "application/json",
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SESSION.get('BearerToken', '')}"
        }

        response = self.session.get(url=url, params=params, headers= h)

        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        body_tag = soup.find('body')
        body_text = body_tag.get_text()
        print(body_text)

    def get_user_profile(self, user_id):
        """
        Fetch user profile information
        """
        url: str =  urljoin(self.config['base_url'], f'rest/v1/profiles', )
        params:str = urllib.parse.urlencode({'id': f'eq.{user_id}', 'select': 'id,project_title,project_status,vehicle_make,vehicle_model,vehicle_year,vision_statement,target_range,target_motor,target_battery_kwh,target_budget,project_image_url,user_id,created_at'})
        h =  {
            "Content-Type": "application/json",
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SESSION.get('BearerToken', '')}"
        }

        print(f"{user_id=}")
        response = self.session.get(url=url, params=params, headers= h)

        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        body_tag = soup.find('body')
        body_text = body_tag.get_text()
        print(body_text)
        SESSION['user_profile'] = response.json()
        
    def create_new_project(self, project_name):
        """
        Create a new project on the website
        """
        print("\n" + "="*60)
        print("Creating New Project")
        print("="*60)
        
        project_data = {
            "user_id":"3aa0cd9c-a501-4e30-b724-e52f380dacc5",
            "cluster_id":"2233c641-866e-460c-ba16-facce4bbdde4",
            "project_title":"1972 Satellite Plymouth",
            "vehicle_make":"Satellite",
            "vehicle_model":"Plymouth",
            "vehicle_year":1972,
            "vision_statement":"This is the vision",
            "target_range":123,
            "target_motor":"Nissan Leaf",
            "target_battery_kwh":31,
            "target_budget":"$30K - $50K",
            "project_status":"Planning"
        }
        
        try:
            response = self.session.post(
                urljoin(self.config['base_url'], '/projects/create'),
                json=project_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                print("✓ Project created successfully!")
                print("Project Details:")
                print(json.dumps(response.json(), indent=2))
                return True
            else:
                print("✗ Failed to create project")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating project: {e}")
            return False

    def login(self, username=None, password=None):
        """
        Attempt to login to the website
        """
        username = username or self.config['username']
        password = password or self.config['password']
               
        print(f"URL: {self.config['login_url']}")        
           
        response = self.session.get(
            self.config['login_url'],
            headers = {
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY
            }
        )
                        
        login_data = {
            'email': username,
            'password': password,             
        }     

        response = self.session.post(
            self.config['login_url'],
            json=login_data,
            allow_redirects=True,
            headers={
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY
            }
        )

        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(response.text)
        response.raise_for_status()
        d =  response.json().get('user', {})
        SESSION['user_id'] = d.get('id', '')
        SESSION['BearerToken'] = response.json().get('access_token', '')

        # Check if login was successful
        # Common indicators: redirect, specific cookies, response content
        if self._check_login_success(response):
            print("\n✓ Login successful!")
            self.authenticated = True
            self._save_session()
            return True
        else:
            print("\n✗ Login may have failed")
            print(f"   Response length: {len(response.text)} bytes")
            
            # Show cookies received
            if self.session.cookies:
                print("\n   Cookies received:")
                for cookie in self.session.cookies:
                    print(f"     - {cookie.name}: {cookie.value[:50]}...")
            
            return False
    
    def _check_login_success(self, response):
        """
        Check if login was successful based on response
        Adjust these checks based on your website's behavior
        """
        # Check 1: Successful redirect away from login page
        if 'login' not in response.url.lower():
            return True
        
        # Check 2: Look for authentication cookies
        auth_cookie_names = ['session', 'token', 'auth', 'jwt', 'sid']
        for cookie in self.session.cookies:
            if any(name in cookie.name.lower() for name in auth_cookie_names):
                return True
        
        # Check 3: Check for common error messages in response
        error_indicators = ['invalid', 'incorrect', 'failed', 'error', 'wrong']
        response_lower = response.text.lower()
        if not any(indicator in response_lower for indicator in error_indicators):
            # No error messages found - might be successful
            if len(self.session.cookies) > 0:
                return True
        
        return False
    
    def _save_session(self):
        """Save session data to file"""
        self.session_data = {
            'cookies': dict(self.session.cookies),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.config['session_file'], 'w') as f:
                json.dump(self.session_data, f, indent=2)
            print(f"✓ Session saved to {self.config['session_file']}")
        except Exception as e:
            print(f"⚠ Could not save session: {e}")
    
    def load_session(self):
        """Load session data from file"""
        try:
            with open(self.config['session_file'], 'r') as f:
                self.session_data = json.load(f)
            
            # Restore cookies
            for name, value in self.session_data.get('cookies', {}).items():
                self.session.cookies.set(name, value)
            
            print(f"✓ Session loaded from {self.config['session_file']}")
            self.authenticated = True
            return True
        except FileNotFoundError:
            print("No saved session found")
            return False
        except Exception as e:
            print(f"⚠ Could not load session: {e}")
            return False
    
    def get(self, path, **kwargs):
        """Make authenticated GET request"""
        url = urljoin(self.config['base_url'], path)
        
        try:
            response = self.session.get(url, **kwargs)
            return response
        except Exception as e:
            print(f"✗ GET request failed: {e}")
            return None
    
    def post(self, path, **kwargs):
        """Make authenticated POST request"""
        url = urljoin(self.config['base_url'], path)
        
        try:
            response = self.session.post(url, **kwargs)
            return response
        except Exception as e:
            print(f"✗ POST request failed: {e}")
            return None

    def show_session_info(self):
        """Display current session information"""
        print("\n" + "="*60)
        print("Session Information")
        print("="*60)
        print(f"Authenticated: {self.authenticated}")
        print(f"\nCookies ({len(self.session.cookies)}):")
        
        if self.session.cookies:
            for cookie in self.session.cookies:
                print(f"  - {cookie.name}: {cookie.value[:50]}{'...' if len(cookie.value) > 50 else ''}")
        else:
            print("  No cookies")
        
        print(f"\nHeaders:")
        for key, value in self.session.headers.items():
            print(f"  - {key}: {value}")
        
        print("="*60 + "\n")
