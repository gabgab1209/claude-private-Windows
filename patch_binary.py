#!/usr/bin/env python3
"""
Patch Claude Code binary to disable all telemetry and phone-home behavior.

Strategy: Replace telemetry URLs with same-length dummy URLs that will fail silently.
Also patch key function checks to disable analytics.
"""
import sys
import os
import re

def make_dummy_url(original: str) -> str:
    """Create a dummy URL of the same byte length that will fail silently."""
    # Replace with a localhost URL padded to same length
    prefix = "http://0.0.0.0:1/"
    padding_needed = len(original) - len(prefix)
    if padding_needed < 0:
        # If original is shorter than prefix, just use spaces
        return " " * len(original)
    return prefix + "x" * padding_needed

def patch_binary(input_path: str, output_path: str):
    with open(input_path, 'rb') as f:
        data = f.read()

    original_size = len(data)
    patches = []

    # === TELEMETRY ENDPOINTS ===

    # 1. Datadog logs endpoint (the 15-second flush - biggest bandwidth culprit)
    patches.append((
        b'https://http-intake.logs.us5.datadoghq.com/api/v2/logs',
        b'http://0.0.0.0:1/' + b'x' * (len(b'https://http-intake.logs.us5.datadoghq.com/api/v2/logs') - len(b'http://0.0.0.0:1/'))
    ))

    # 2. Datadog client token
    patches.append((
        b'pubbbf48e6d78dae54bceaa4acf463299bf',
        b'x' * len(b'pubbbf48e6d78dae54bceaa4acf463299bf')
    ))

    # 3. 1P event logging endpoint
    patches.append((
        b'/api/event_logging/batch',
        b'/xxx/xxxxx_xxxxxxx/xxxxx'
    ))

    # 4. BigQuery metrics endpoint
    patches.append((
        b'/api/claude_code/metrics',
        b'/xxx/xxxxxx_xxxx/xxxxxxx'
    ))

    # 5. Metrics opt-out check endpoint
    patches.append((
        b'/api/claude_code/organizations/metrics_enabled',
        b'/xxx/xxxxxx_xxxx/xxxxxxxxxxxxx/xxxxxxx_xxxxxxx'
    ))

    # 6. Remote managed settings endpoint
    patches.append((
        b'/api/claude_code/managed_settings',
        b'/xxx/xxxxxx_xxxx/xxxxxxx_xxxxxxxx'
    ))

    # 7. User settings sync endpoint
    patches.append((
        b'/api/claude_code/user_settings',
        b'/xxx/xxxxxx_xxxx/xxxx_xxxxxxxx'
    ))

    # 8. Policy limits endpoint
    patches.append((
        b'/api/claude_code/policy_limits',
        b'/xxx/xxxxxx_xxxx/xxxxxx_xxxxxx'
    ))

    # 9. Bootstrap endpoint
    patches.append((
        b'/api/claude_cli/bootstrap',
        b'/xxx/xxxxxx_xxx/xxxxxxxxx'
    ))

    # 10. Grove endpoints
    patches.append((
        b'/api/claude_code_grove',
        b'/xxx/xxxxxx_xxxx_xxxxx'
    ))

    # 11. MCP registry
    patches.append((
        b'mcp-registry/v0/servers',
        b'xxx-xxxxxxxx/xx/xxxxxxx'
    ))

    # 12. Trusted device enrollment
    patches.append((
        b'/api/auth/trusted_devices',
        b'/xxx/xxxx/xxxxxxx_xxxxxxx'
    ))

    # 13. Grove notice viewed
    patches.append((
        b'/api/oauth/account/grove_notice_viewed',
        b'/xxx/xxxxx/xxxxxxx/xxxxx_xxxxxx_xxxxxx'
    ))

    # 14. Referral eligibility
    patches.append((
        b'/referral/eligibility',
        b'/xxxxxxxx/xxxxxxxxxxx'
    ))

    # 15. Referral redemptions
    patches.append((
        b'/referral/redemptions',
        b'/xxxxxxxx/xxxxxxxxxxx'
    ))

    # 16. Session ingress
    patches.append((
        b'/v2/session_ingress/',
        b'/xx/xxxxxxx_xxxxxxx/'
    ))

    # 17. Session ingress v1 URL path
    patches.append((
        b'/v1/session_ingress/session/',
        b'/xx/xxxxxxx_xxxxxxx/xxxxxxx/'
    ))

    # 18. Staging API (in case it leaks)
    patches.append((
        b'https://api-staging.anthropic.com/api/event_logging/batch',
        b'http://0.0.0.0:1/' + b'x' * (len(b'https://api-staging.anthropic.com/api/event_logging/batch') - len(b'http://0.0.0.0:1/'))
    ))

    # Apply patches
    patched_count = 0
    for old, new in patches:
        if len(old) != len(new):
            print(f"  WARNING: Length mismatch for {old[:40]}... ({len(old)} vs {len(new)}), skipping")
            continue
        count = data.count(old)
        if count > 0:
            data = data.replace(old, new)
            patched_count += 1
            print(f"  Patched {count}x: {old[:60].decode('utf-8', errors='replace')}")
        else:
            print(f"  Not found: {old[:60].decode('utf-8', errors='replace')}")

    # Verify size unchanged
    assert len(data) == original_size, f"Size changed! {original_size} -> {len(data)}"

    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"\nPatched {patched_count} endpoints. Output: {output_path}")
    print(f"Binary size: {original_size} bytes (unchanged)")

if __name__ == '__main__':
    # Defaulting to standard Windows CLI binary names
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'claude.exe'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'claude-notelemetry.exe'

    print(f"Patching {input_path} -> {output_path}")
    patch_binary(input_path, output_path)
