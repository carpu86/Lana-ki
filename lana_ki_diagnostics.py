#!/usr/bin/env python3
# =================================================================
# LANA-KI COMPREHENSIVE DIAGNOSTICS
# Vollständige System- und API-Diagnose
# =================================================================

import requests
import json
import sys
import subprocess
import time
from datetime import datetime
import os

class LanaKIDiagnostics:
    def __init__(self):
        self.config = {
            # API Keys
            'GEMINI_KEY': 'AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA',
            'OPENAI_KEY': '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',
            'GITHUB_TOKEN': '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',
            'CF_TOKEN': 'cfat_9EQccufEvVK3fhEMjENP5gOT9zGBVDeDz8r87Io4be9d2058',
            
            # Infrastructure
            'DEBIAN_IP': '192.168.178.103',
            'GATEWAY_URL': 'https://gateway.lana-ki.de',
            'DOMAIN': 'lana-ki.de',
            'CF_ZONE_ID': '8e0b1cf2a7d31dbf35e852bbf7978f8d',
            'CF_ACCOUNT_ID': '4b7829c229e797cbb030c5e1016c7363'
        }
        
        self.results = {}
        self.start_time = datetime.now()
    
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_test(self, name, status, details=""):
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}: {'PASS' if status else 'FAIL'}")
        if details:
            print(f"   {details}")
        self.results[name] = {'status': status, 'details': details}
    
    def test_gemini_api(self):
        """Test Gemini API with multiple endpoints"""
        print("\n🧪 Testing Gemini API...")
        
        endpoints = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        for endpoint in endpoints:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{endpoint}:generateContent"
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "contents": [{
                        "parts": [{"text": "Respond with 'API Working'"}]
                    }]
                }
                
                response = requests.post(
                    f"{url}?key={self.config['GEMINI_KEY']}", 
                    json=payload, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and data['candidates']:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        self.print_test(f"Gemini {endpoint}", True, f"Response: {text[:50]}...")
                        return True
                    else:
                        self.print_test(f"Gemini {endpoint}", False, "No candidates in response")
                else:
                    self.print_test(f"Gemini {endpoint}", False, f"HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                self.print_test(f"Gemini {endpoint}", False, str(e))
        
        return False
    
    def test_openai_api(self):
        """Test OpenAI API"""
        print("\n🧪 Testing OpenAI API...")
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['OPENAI_KEY']}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Say 'API Working'"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content']
                self.print_test("OpenAI API", True, f"Response: {message}")
                return True
            else:
                self.print_test("OpenAI API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("OpenAI API", False, str(e))
            return False
    
    def test_github_api(self):
        """Test GitHub API"""
        print("\n🧪 Testing GitHub API...")
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['GITHUB_TOKEN']}",
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("GitHub API", True, f"User: {data.get('login', 'Unknown')}")
                return True
            else:
                self.print_test("GitHub API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("GitHub API", False, str(e))
            return False
    
    def test_cloudflare_api(self):
        """Test Cloudflare API"""
        print("\n🧪 Testing Cloudflare API...")
        
        try:
            headers = {
                'Authorization': f"Bearer {self.config['CF_TOKEN']}",
                'Content-Type': 'application/json'
            }
            
            # Test zone access
            response = requests.get(
                f"https://api.cloudflare.com/client/v4/zones/{self.config['CF_ZONE_ID']}", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                zone_name = data['result']['name']
                zone_status = data['result']['status']
                self.print_test("Cloudflare API", True, f"Zone: {zone_name} ({zone_status})")
                return True
            else:
                self.print_test("Cloudflare API", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("Cloudflare API", False, str(e))
            return False
    
    def test_debian_server(self):
        """Test Debian server connectivity"""
        print("\n🧪 Testing Debian Server...")
        
        try:
            # Test SSH connectivity
            result = subprocess.run(
                ['ssh', '-o', 'ConnectTimeout=10', f"carpu@{self.config['DEBIAN_IP']}", 'echo "SSH_OK"'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and 'SSH_OK' in result.stdout:
                self.print_test("SSH Connection", True, "Connected successfully")
                
                # Test PM2 status
                pm2_result = subprocess.run(
                    ['ssh', f"carpu@{self.config['DEBIAN_IP']}", 'pm2 status --no-color'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if pm2_result.returncode == 0:
                    lines = pm2_result.stdout.split('\n')
                    online_count = sum(1 for line in lines if 'online' in line)
                    self.print_test("PM2 Services", True, f"{online_count} services online")
                else:
                    self.print_test("PM2 Services", False, "PM2 not responding")
                
                return True
            else:
                self.print_test("SSH Connection", False, "Connection failed")
                return False
                
        except Exception as e:
            self.print_test("Debian Server", False, str(e))
            return False
    
    def test_gateway(self):
        """Test Gateway connectivity"""
        print("\n🧪 Testing Gateway...")
        
        try:
            response = requests.get(self.config['GATEWAY_URL'], timeout=15)
            
            if response.status_code == 200:
                self.print_test("Gateway", True, f"HTTP {response.status_code}")
                return True
            else:
                self.print_test("Gateway", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.print_test("Gateway", False, "Connection timeout")
            return False
        except requests.exceptions.ConnectionError:
            self.print_test("Gateway", False, "Connection error (DNS/Network)")
            return False
        except Exception as e:
            self.print_test("Gateway", False, str(e))
            return False
    
    def test_dns_resolution(self):
        """Test DNS resolution"""
        print("\n🧪 Testing DNS Resolution...")
        
        domains = [
            'lana-ki.de',
            'gateway.lana-ki.de',
            'google.com'
        ]
        
        all_passed = True
        for domain in domains:
            try:
                import socket
                socket.gethostbyname(domain)
                self.print_test(f"DNS {domain}", True, "Resolved successfully")
            except Exception as e:
                self.print_test(f"DNS {domain}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_network_connectivity(self):
        """Test basic network connectivity"""
        print("\n🧪 Testing Network Connectivity...")
        
        hosts = [
            ('Google DNS', '8.8.8.8'),
            ('Cloudflare DNS', '1.1.1.1'),
            ('GitHub', 'github.com'),
            ('OpenAI', 'api.openai.com')
        ]
        
        all_passed = True
        for name, host in hosts:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                if host.replace('.', '').isdigit():  # IP address
                    result = sock.connect_ex((host, 53))  # DNS port
                else:  # Domain name
                    result = sock.connect_ex((host, 443))  # HTTPS port
                
                sock.close()
                
                if result == 0:
                    self.print_test(f"Network {name}", True, "Reachable")
                else:
                    self.print_test(f"Network {name}", False, "Unreachable")
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"Network {name}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.print_header("DIAGNOSTIC REPORT")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['status'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔧 Failed Tests:")
            for name, result in self.results.items():
                if not result['status']:
                    print(f"   ❌ {name}: {result['details']}")
        
        duration = datetime.now() - self.start_time
        print(f"\n⏱️ Diagnostic completed in {duration.total_seconds():.1f} seconds")
        
        # Save report to file
        report_file = f"lana_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': self.start_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        self.print_header("LANA-KI SYSTEM DIAGNOSTICS")
        print(f"🕐 Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Network tests first
        self.test_network_connectivity()
        self.test_dns_resolution()
        
        # API tests
        self.test_gemini_api()
        self.test_openai_api()
        self.test_github_api()
        self.test_cloudflare_api()
        
        # Infrastructure tests
        self.test_debian_server()
        self.test_gateway()
        
        # Generate final report
        self.generate_report()

def main():
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        diagnostics = LanaKIDiagnostics()
        
        if test_name == 'gemini':
            diagnostics.test_gemini_api()
        elif test_name == 'openai':
            diagnostics.test_openai_api()
        elif test_name == 'github':
            diagnostics.test_github_api()
        elif test_name == 'cloudflare':
            diagnostics.test_cloudflare_api()
        elif test_name == 'debian':
            diagnostics.test_debian_server()
        elif test_name == 'gateway':
            diagnostics.test_gateway()
        elif test_name == 'network':
            diagnostics.test_network_connectivity()
        elif test_name == 'dns':
            diagnostics.test_dns_resolution()
        else:
            print(f"❌ Unknown test: {test_name}")
            print("Available tests: gemini, openai, github, cloudflare, debian, gateway, network, dns")
    else:
        # Run all tests
        diagnostics = LanaKIDiagnostics()
        diagnostics.run_all_tests()

if __name__ == "__main__":
    main()
