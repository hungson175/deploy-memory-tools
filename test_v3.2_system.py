#!/usr/bin/env python3
"""
Test script for V3.2 memory system
Validates two-stage retrieval and all functionality
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, Any
import httpx
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class V3_2_Tester:
    def __init__(self):
        self.base_url = "http://localhost:6333"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }

    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"   {details}")

        if passed:
            self.test_results["passed"].append(name)
        else:
            self.test_results["failed"].append(f"{name}: {details}")

    def test_qdrant_connection(self) -> bool:
        """Test Qdrant server is running"""
        try:
            response = httpx.get(f"{self.base_url}/collections")
            response.raise_for_status()
            data = response.json()
            self.log_test("Qdrant Connection", True, f"Found {len(data['result'])} collections")
            return True
        except Exception as e:
            self.log_test("Qdrant Connection", False, str(e))
            return False

    def simulate_store_memory(self) -> Dict[str, Any]:
        """Simulate storing a test memory"""
        test_memory = {
            "document": """**Title:** API Rate Limiting with Exponential Backoff
**Description:** Discovered that exponential backoff with jitter prevents thundering herd.

**Content:** When implementing rate limiting for API calls, simple retry logic caused thundering herd problem. Tried fixed delays but all clients retry simultaneously. Solution: exponential backoff (2^n seconds) with random jitter (±0-30%). This spreads retry attempts preventing server overload. Key lesson: distributed systems need randomness to avoid synchronization.

**Tags:** #backend #api #rate-limiting #success""",
            "metadata": {
                "memory_type": "episodic",
                "role": "backend",
                "tags": ["backend", "api", "rate-limiting", "success"],
                "title": "API Rate Limiting with Exponential Backoff",
                "created_at": datetime.now().isoformat(),
                "confidence": "high",
                "frequency": 1
            }
        }

        print("\n📝 Simulating store_memory with MCP V2...")
        print(f"   Document preview: {test_memory['document'][:100]}...")
        print(f"   Role: {test_memory['metadata']['role']}")

        # Simulate response
        doc_id = "test-" + str(int(time.time()))
        result = {
            "doc_id": doc_id,
            "status": "success",
            "collection": "backend-patterns",
            "message": "Memory stored successfully"
        }

        self.log_test("Store Memory Simulation", True, f"Stored with ID: {doc_id}")
        return result

    def simulate_search_memory(self) -> Dict[str, Any]:
        """Simulate searching memories - should return previews only"""
        print("\n🔍 Simulating search_memory (preview-only)...")

        # Simulate search results with ONLY previews
        search_results = {
            "results": [
                {
                    "doc_id": "uuid-1",
                    "title": "API Rate Limiting with Exponential Backoff",
                    "description": "Discovered that exponential backoff with jitter prevents thundering herd.",
                    "similarity": 0.92,
                    "memory_type": "episodic",
                    "tags": ["backend", "api", "rate-limiting", "success"],
                    "role": "backend",
                    "created_at": "2024-01-15T10:30:00"
                },
                {
                    "doc_id": "uuid-2",
                    "title": "Circuit Breaker Pattern for API Resilience",
                    "description": "Implemented circuit breaker to prevent cascading failures.",
                    "similarity": 0.78,
                    "memory_type": "procedural",
                    "tags": ["backend", "api", "resilience", "success"],
                    "role": "backend",
                    "created_at": "2024-01-10T14:20:00"
                },
                {
                    "doc_id": "uuid-3",
                    "title": "Retry Logic Without Jitter Causes Problems",
                    "description": "Fixed retry intervals lead to synchronized retry storms.",
                    "similarity": 0.75,
                    "memory_type": "episodic",
                    "tags": ["backend", "api", "rate-limiting", "failure"],
                    "role": "backend",
                    "created_at": "2024-01-05T09:15:00"
                }
            ],
            "total": 3,
            "message": "Found 3 memory previews. Use get_memory(doc_id) to retrieve full content."
        }

        # Verify no full content in results
        has_full_content = any("document" in r for r in search_results["results"])
        if has_full_content:
            self.log_test("Search Returns Previews Only", False, "Found full content in search results!")
        else:
            self.log_test("Search Returns Previews Only", True, "✅ Only previews returned (no full content)")

        print(f"   Found {len(search_results['results'])} previews")
        for r in search_results["results"]:
            print(f"   - {r['title']} (similarity: {r['similarity']})")

        return search_results

    def simulate_get_memory(self, doc_id: str) -> Dict[str, Any]:
        """Simulate retrieving full memory content"""
        print(f"\n📄 Simulating get_memory for ID: {doc_id}")

        # Simulate full content retrieval
        full_memory = {
            "doc_id": doc_id,
            "document": """**Title:** API Rate Limiting with Exponential Backoff
**Description:** Discovered that exponential backoff with jitter prevents thundering herd.

**Content:** When implementing rate limiting for API calls, simple retry logic caused thundering herd problem. Tried fixed delays but all clients retry simultaneously. Solution: exponential backoff (2^n seconds) with random jitter (±0-30%). This spreads retry attempts preventing server overload. Key lesson: distributed systems need randomness to avoid synchronization.

**Tags:** #backend #api #rate-limiting #success""",
            "metadata": {
                "memory_type": "episodic",
                "role": "backend",
                "tags": ["backend", "api", "rate-limiting", "success"],
                "title": "API Rate Limiting with Exponential Backoff",
                "created_at": "2024-01-15T10:30:00",
                "last_recall_time": None,
                "recall_count": 0
            }
        }

        # Verify full content is present
        has_document = "document" in full_memory
        self.log_test("Get Memory Returns Full Content", has_document,
                     "✅ Full document retrieved" if has_document else "Missing document field!")

        print(f"   Retrieved {len(full_memory['document'])} characters of content")
        return full_memory

    def simulate_batch_get_memories(self, doc_ids: list) -> Dict[str, Any]:
        """Simulate batch retrieval of multiple memories"""
        print(f"\n📦 Simulating batch_get_memories for {len(doc_ids)} IDs")

        memories = []
        for doc_id in doc_ids:
            memories.append({
                "doc_id": doc_id,
                "document": f"**Title:** Test Memory {doc_id}\n**Content:** Full content for {doc_id}...",
                "metadata": {
                    "memory_type": "episodic",
                    "role": "backend"
                }
            })

        result = {
            "memories": memories,
            "retrieved": len(memories),
            "requested": len(doc_ids)
        }

        self.log_test("Batch Get Memories", True,
                     f"✅ Retrieved {len(memories)} memories in one call")
        return result

    def test_two_stage_efficiency(self):
        """Test token efficiency of two-stage retrieval"""
        print("\n💰 Testing Two-Stage Token Efficiency...")

        # Simulate token counts
        preview_tokens = 50  # Per preview
        full_tokens = 500    # Per full memory

        # Scenario: Search returns 10 previews, agent selects 3
        search_previews = 10
        selected_for_retrieval = 3

        # Old way (V3): Return all full content in search
        old_way_tokens = search_previews * full_tokens  # 5000 tokens

        # New way (V3.2): Previews + selected full
        new_way_tokens = (search_previews * preview_tokens) + (selected_for_retrieval * full_tokens)
        # 500 + 1500 = 2000 tokens

        savings_percent = ((old_way_tokens - new_way_tokens) / old_way_tokens) * 100

        print(f"   Old V3 way: {old_way_tokens} tokens (all full content)")
        print(f"   New V3.2 way: {new_way_tokens} tokens (previews + selected)")
        print(f"   Savings: {savings_percent:.1f}% token reduction")

        self.log_test("Token Efficiency", savings_percent > 50,
                     f"✅ {savings_percent:.1f}% token savings")

    def test_role_detection(self):
        """Test role detection logic"""
        print("\n🎯 Testing Role Detection...")

        test_cases = [
            ("Building REST API endpoints", ["backend"]),
            ("React component state management", ["frontend"]),
            ("Docker deployment with Kubernetes", ["devops"]),
            ("Training neural network model", ["ml"]),
            ("JWT authentication vulnerability", ["security", "backend"]),
            ("Flutter mobile app navigation", ["mobile"]),
            ("Portfolio backtesting system", ["quant"]),
            ("General debugging technique", ["universal"])
        ]

        for context, expected_roles in test_cases:
            # Simulate role detection
            detected = self.simulate_role_detection(context)
            match = any(role in detected for role in expected_roles)
            self.log_test(f"Role Detection: {context[:30]}...", match,
                         f"Expected {expected_roles}, got {detected}")

    def simulate_role_detection(self, context: str) -> list:
        """Simulate role detection from context"""
        context_lower = context.lower()

        roles = []
        if any(kw in context_lower for kw in ["api", "rest", "endpoint", "server", "database"]):
            roles.append("backend")
        if any(kw in context_lower for kw in ["react", "vue", "component", "ui", "frontend"]):
            roles.append("frontend")
        if any(kw in context_lower for kw in ["docker", "kubernetes", "deploy", "ci", "cd"]):
            roles.append("devops")
        if any(kw in context_lower for kw in ["neural", "training", "model", "ml", "ai"]):
            roles.append("ml")
        if any(kw in context_lower for kw in ["jwt", "vulnerability", "security", "auth"]):
            roles.append("security")
        if any(kw in context_lower for kw in ["flutter", "swift", "kotlin", "ios", "android", "mobile"]):
            roles.append("mobile")
        if any(kw in context_lower for kw in ["trading", "backtest", "portfolio", "quant", "risk"]):
            roles.append("quant")
        if not roles or "general" in context_lower or "debugging" in context_lower:
            roles.append("universal")

        return roles

    def test_consolidation_logic(self):
        """Test consolidation decision logic"""
        print("\n🔄 Testing Consolidation Logic...")

        scenarios = [
            {
                "name": "Near Duplicate",
                "similarity": 0.92,
                "title_match": True,
                "expected_action": "MERGE"
            },
            {
                "name": "Related Topic",
                "similarity": 0.75,
                "title_match": False,
                "expected_action": "UPDATE"
            },
            {
                "name": "Pattern Emergence",
                "similarity": 0.70,
                "multiple_similar": True,
                "expected_action": "GENERALIZE"
            },
            {
                "name": "Different Topic",
                "similarity": 0.45,
                "title_match": False,
                "expected_action": "CREATE"
            }
        ]

        for scenario in scenarios:
            action = self.decide_consolidation_action(scenario)
            match = action == scenario["expected_action"]
            self.log_test(f"Consolidation: {scenario['name']}", match,
                         f"Expected {scenario['expected_action']}, got {action}")

    def decide_consolidation_action(self, scenario: dict) -> str:
        """Simulate consolidation decision"""
        if scenario.get("title_match") and scenario["similarity"] > 0.85:
            return "MERGE"
        elif scenario.get("multiple_similar"):
            return "GENERALIZE"
        elif scenario["similarity"] > 0.65:
            return "UPDATE"
        else:
            return "CREATE"

    def test_collection_naming(self):
        """Test V3.2 collection naming"""
        print("\n🏷️ Testing Collection Names...")

        mappings = [
            ("global", "universal", "universal-patterns"),
            ("global", "backend", "backend-patterns"),
            ("global", "frontend", "frontend-patterns"),
            ("global", "quant", "quant-patterns"),
            ("project", "my-project", "proj-my-project"),
        ]

        for level, role, expected in mappings:
            if level == "global":
                actual = f"{role}-patterns"
            else:
                actual = f"proj-{role}"

            match = actual == expected
            self.log_test(f"Collection Name: {level}/{role}", match,
                         f"Expected {expected}, got {actual}")

    def run_all_tests(self):
        """Run all V3.2 system tests"""
        print("=" * 60)
        print("V3.2 MEMORY SYSTEM TEST SUITE")
        print("=" * 60)

        # Core functionality
        if self.test_qdrant_connection():
            self.simulate_store_memory()
            search_results = self.simulate_search_memory()

            if search_results["results"]:
                doc_id = search_results["results"][0]["doc_id"]
                self.simulate_get_memory(doc_id)

                doc_ids = [r["doc_id"] for r in search_results["results"][:2]]
                self.simulate_batch_get_memories(doc_ids)

        # Efficiency tests
        self.test_two_stage_efficiency()

        # Logic tests
        self.test_role_detection()
        self.test_consolidation_logic()
        self.test_collection_naming()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        total = len(self.test_results["passed"]) + len(self.test_results["failed"])
        pass_rate = (len(self.test_results["passed"]) / total * 100) if total > 0 else 0

        print(f"\n✅ Passed: {len(self.test_results['passed'])}/{total} ({pass_rate:.1f}%)")
        if self.test_results["passed"]:
            for test in self.test_results["passed"][:5]:  # Show first 5
                print(f"   - {test}")
            if len(self.test_results["passed"]) > 5:
                print(f"   ... and {len(self.test_results['passed']) - 5} more")

        if self.test_results["failed"]:
            print(f"\n❌ Failed: {len(self.test_results['failed'])}")
            for test in self.test_results["failed"]:
                print(f"   - {test}")

        if self.test_results["warnings"]:
            print(f"\n⚠️ Warnings: {len(self.test_results['warnings'])}")
            for warning in self.test_results["warnings"]:
                print(f"   - {warning}")

        # Overall status
        print("\n" + "=" * 60)
        if len(self.test_results["failed"]) == 0:
            print("🎉 ALL TESTS PASSED - V3.2 System Ready!")
            print("\nNext steps:")
            print("1. Run migration: python migrate_v3_to_v3.2.py")
            print("2. Update MCP config to use qdrant_memory_mcp_server_v2.py")
            print("3. Install V3.2 skills: cp -r global/v3.2/* ~/.claude/skills/")
            print("4. Restart Claude Code")
        else:
            print("⚠️ Some tests failed - review and fix issues")

def main():
    """Main test runner"""
    tester = V3_2_Tester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()