import os
import re
import glob

def refactor_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    # Skip login page
    if 'login.html' in path:
        return
        
    # Replace aside block
    content = re.sub(r'<aside.*?</aside>', '{% include "components/sidebar.html" %}', content, flags=re.DOTALL)
    
    # Replace header block
    content = re.sub(r'<header.*?</header>', '{% include "components/navbar.html" %}', content, flags=re.DOTALL)
    
    with open(path, 'w') as f:
        f.write(content)
    print(f"Refactored: {path}")

# Run for all HTML files
for file in glob.glob('templates/**/*.html', recursive=True):
    refactor_file(file)
