# Qdrant Scoring Test - FULL CONTENT Analysis

**Date:** 2026-01-07
**Collection:** universal-patterns
**Total Memories:** 91

================================================================================

## Test Results

| Measurement | Score |
|-------------|-------|
| Manual cosine similarity (A vs B) | `0.897777` |
| Qdrant score (A vs B) | `0.897777` |
| Qdrant score (A vs A - self) | `1.000000` |

## Conclusion

**✅ Qdrant uses SIMILARITY scoring**

- Score of 1.0 = identical vectors
- Higher scores = more similar
- Score range: [-1, 1] for cosine similarity

================================================================================

## Memory A - FULL CONTENT

**ID:** `282a1048-f358-40a5-b789-2464d9c3472f`
**Vector Dimension:** 1536

**FULL DOCUMENT:**
```
**Title:** Corporate Network Blocking Git SSH Connections
**Description:** Git push/pull failed with SSH timeout on corporate network blocking external SSH port 22 connections.

**Content:** Attempted `git push` on company network, got "kex_exchange_identification: read: Operation timed out" connecting to GitHub (20.205.243.166:22). Corporate firewalls commonly block SSH (port 22) to external hosts as security policy. User explicitly stated "let me change the network, my company network won't connect to github" and resolved by switching to non-corporate network. Workarounds: (1) switch to home/mobile network (simplest), (2) use GitHub HTTPS instead of SSH (`git remote set-url origin https://...`), (3) configure SSH over HTTPS port 443 in ~/.ssh/config, or (4) use corporate VPN/proxy if available. Critical: always commit changes locally first so work is safe while troubleshooting network issues. Lesson: SSH connection timeouts to git hosts on corporate networks almost always indicate firewall blocking port 22, not git or SSH misconfiguration.

**Tags:** #episodic #git #ssh #corporate-network #firewall #port-22 #timeout #networking #troubleshooting #failure-then-success
```

================================================================================

## Memory B - FULL CONTENT

**ID:** `cd6adfa1-7bac-4768-8ae0-32e6ded68a56`
**Vector Dimension:** 1536

**FULL DOCUMENT:**
```
**Title:** Diagnosing and Fixing Corporate Network Git SSH Blocking
**Description:** Systematic workflow to diagnose and fix git push/pull timeouts caused by corporate firewall blocking SSH port 22.

**Content:** When `git push` or `git pull` fails with "kex_exchange_identification: read: Operation timed out" or "banner exchange: Connection to <IP> port 22: Operation timed out", suspect corporate firewall blocking SSH port 22. First, commit changes locally (`git commit`) so work is safe. Then test: attempt `ssh -T git@github.com` - if this times out, confirms SSH blocking not git issue. Solutions in order of simplicity: (1) Switch to non-corporate network (home WiFi/mobile hotspot) and retry, (2) Switch from SSH to HTTPS (`git remote set-url origin https://github.com/user/repo.git`), (3) Configure SSH over HTTPS port 443 by adding to ~/.ssh/config: `Host github.com\n  Hostname ssh.github.com\n  Port 443`, or (4) Use corporate VPN/proxy if provided. Always test with `ssh -T git@github.com` after changes to confirm connectivity before retrying git operations.

**Tags:** #procedural #git #ssh #corporate-firewall #troubleshooting #networking #port-22 #https #workaround #success
```

================================================================================

## Why Are They Similar?

These two memories have a cosine similarity of **0.897777**.

Compare the full content above to see what semantic patterns make them similar.

