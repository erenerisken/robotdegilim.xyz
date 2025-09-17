#!/usr/bin/env python3
import requests

def main():
    print("🔍 Checking NTE result...")
    
    try:
        response = requests.get('https://robotd.s3.eu-central-1.amazonaws.com/nte-available.json')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total NTE courses: {len(data)}")
            
            if len(data) > 0:
                print("\n📚 Sample courses:")
                for i, course in enumerate(data[:5]):
                    code = course.get('code', {})
                    dept_code = code.get('departmental', 'N/A')
                    name = course.get('name', 'N/A')[:60]
                    sections = len(course.get('sections', []))
                    print(f"  {i+1}. {dept_code} - {name}... ({sections} sections)")
            else:
                print("❌ No NTE courses found")
        else:
            print(f"❌ Failed to fetch: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 