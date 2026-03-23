import re
import codecs
import subprocess
import os

src_path = "/Users/zencefilefendi/Desktop/namaz/Diyanet_Offline_Motor_src.html"
prod_path = "/Users/zencefilefendi/Desktop/namaz/Diyanet_Offline_Motor.html"

# If src doesn't exist, this is the first time. We copy from prod to src.
if not os.path.exists(src_path):
    with codecs.open(prod_path, "r", "utf-8") as f:
        content = f.read()
    with codecs.open(src_path, "w", "utf-8") as f:
        f.write(content)
else:
    with codecs.open(src_path, "r", "utf-8") as f:
        content = f.read()

# The logic script is the second <script> block and ends with </script>
# Let's find exactly the script that has "let currentView = 'daily';"
match = re.search(r'(<script>\s*let currentView =.*?)(</script>)', content, re.DOTALL)
if not match:
    # Try finding any script with getTimes
    match = re.search(r'(<script>\s*.*?(?:function getTimes|let getTimes).*?)(</script>)', content, re.DOTALL)

if not match:
    print("Could not find logic script block!")
    exit(1)

full_script_block = match.group(1)
logic_js = full_script_block.replace("<script>", "", 1)

# Write to logic_temp.js
with codecs.open("logic_temp.js", "w", "utf-8") as f:
    f.write(logic_js)

# Call npx javascript-obfuscator
print("Running javascript-obfuscator (this might take a few seconds)...")
try:
    subprocess.run(["npx", "javascript-obfuscator", "logic_temp.js", "--output", "logic_obf.js", 
                    "--compact", "true", 
                    "--control-flow-flattening", "true",
                    "--dead-code-injection", "true",
                    "--string-array", "true",
                    "--string-array-encoding", "base64",
                    "--string-array-threshold", "1"], check=True)
except subprocess.CalledProcessError as e:
    print("Error during obfuscation:", e)
    exit(1)

# Read obfuscated
with codecs.open("logic_obf.js", "r", "utf-8") as f:
    obf_js = f.read()

# Replace in content for the prod version
# We replace the entire match.group(0) which is <script>...</script>
new_script_block = "<script>\n" + obf_js + "\n" + match.group(2)
prod_content = content.replace(match.group(0), new_script_block)

with codecs.open(prod_path, "w", "utf-8") as f:
    f.write(prod_content)

# Clean up
os.remove("logic_temp.js")
os.remove("logic_obf.js")

print("Successfully generated obfuscated production file!")
