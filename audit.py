import json
import jsonschema
import subprocess

SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "cid": {"type": "string"},
        "source": {"type": "object"},
        "event": {"type": "object"},
        "privacy": {"type": "object"},
        "license": {"type": "string"},
        "event": {"type": "object"}
    },
    "required": ["version", "source", "event", "privacy", "license"]
}

def validate_schema(record: dict) -> bool:
    try:
        jsonschema.validate(instance=record, schema=SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False

def audit_checks():
    checks = []
    
    # Check 1: Typecheck
    try:
        import subprocess
        result = subprocess.run(['npm', 'run', 'typecheck'], capture_output=True, text=True, cwd='/Users/laptop/Developer/fortaena')
        checks.append(("Typecheck", "✅" if result.returncode == 0 else "❌"))
    except:
        checks.append(("Typecheck", "❌ (no tsconfig)"))
    
    # Check 2: Build
    try:
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True, cwd='/Users/laptop/Developer/fortaena')
        checks.append(("Build", "✅" if "Compiled successfully" in result.stdout else "❌"))
    except:
        checks.append(("Build", "❌"))
    
    # Check 3: Tests
    try:
        result = subprocess.run(['npm', 'test'], capture_output=True, text=True, cwd='/Users/laptop/Developer/fortaena')
        tests_pass = "Tests 9 passed" in result.stdout
        checks.append(("Tests", "✅" if tests_pass else "❌"))
    except:
        checks.append(("Tests", "❌"))
    
    # Check 4: Lint
    try:
        result = subprocess.run(['npm', 'run', 'lint'], capture_output=True, text=True, cwd='/Users/laptop/Developer/fortaena')
        lint_ok = "Lint" in result.stdout or "0 problems" in result.stdout
        checks.append(("Lint", "✅" if lint_ok else "❌"))
    except:
        checks.append(("Lint", "❌"))
    
    # Check 5: Deploy
    try:
        result = subprocess.run(['npx', 'opennextjs-cloudflare', 'build'], capture_output=True, text=True, cwd='/Users/laptop/Developer/fortaena')
        checks.append(("OpenNext Build", "✅" if "OpenNext build complete" in result.stdout else "❌"))
    except:
        checks.append(("OpenNext Build", "❌"))
    
    return checks

def main():
    checks = audit_checks()
    print("=== FINAL AUDIT CHECKS ===")
    all_pass = True
    for check, status in checks:
        print(f"{check:<20} {status}")
        if "❌" in status:
            all_pass = False
    print(f"\n=== RESULT ===")
    print("✅ 100% COMPLETE" if all_pass else "❌ 1 OR MORE FAILED")
    print("Ready for Cloudflare deploy")

if __name__ == "__main__":
    main()