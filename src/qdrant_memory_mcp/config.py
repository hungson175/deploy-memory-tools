"""
Configuration for Qdrant Memory MCP Server
"""

import os
from typing import Dict

# Load from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_storage")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Role-based collections mapping
ROLE_COLLECTIONS: Dict[str, Dict[str, str]] = {
    "global": {
        "universal": "universal-patterns",      # Cross-domain patterns
        "backend": "backend-patterns",          # Backend engineering
        "frontend": "frontend-patterns",        # Frontend engineering
        "quant": "quant-patterns",              # Quantitative finance
        "devops": "devops-patterns",           # DevOps and infrastructure
        "ml": "ml-patterns",                   # Machine learning
        "security": "security-patterns",        # Security engineering
        "mobile": "mobile-patterns",           # Mobile development
    },
    "project": {
        # Project collections are created dynamically with pattern: proj-{sanitized-name}
    }
}
