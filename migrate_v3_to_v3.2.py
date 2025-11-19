#!/usr/bin/env python3
"""
Migration script from V3 to V3.2 memory system
Migrates collections to new simplified names and structure
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Collection mapping from V3 to V3.2
COLLECTION_MAPPING = {
    # V3 name -> V3.2 name
    "coder-memory": "universal-patterns",
    "backend-dev": "backend-patterns",
    "frontend-dev": "frontend-patterns",
    "financial-engineer": "quant-patterns",

    # Additional collections that might exist
    "coder": "universal-patterns",  # Alternate name
    "quant": "quant-patterns",      # Alternate name
}

# New collections to create (not in V3)
NEW_COLLECTIONS = [
    "devops-patterns",
    "ml-patterns",
    "security-patterns",
    "mobile-patterns"
]

class MigrationManager:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.migration_report = {
            "collections_migrated": [],
            "collections_created": [],
            "memories_migrated": 0,
            "errors": []
        }

    def get_existing_collections(self) -> List[str]:
        """Get list of existing collections"""
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            return []

    def create_v3_2_collection(self, name: str) -> bool:
        """Create a V3.2 collection if it doesn't exist"""
        try:
            # Check if exists
            try:
                self.client.get_collection(name)
                logger.info(f"Collection '{name}' already exists")
                return True
            except:
                pass

            # Create new collection
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=1536,  # text-embedding-3-small dimension
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created V3.2 collection: {name}")
            self.migration_report["collections_created"].append(name)
            return True

        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            self.migration_report["errors"].append(f"Create {name}: {str(e)}")
            return False

    def migrate_collection(self, old_name: str, new_name: str) -> int:
        """Migrate memories from old collection to new"""
        try:
            # Check if old collection exists
            try:
                old_info = self.client.get_collection(old_name)
                total_points = old_info.points_count
                logger.info(f"Found {total_points} memories in '{old_name}'")
            except:
                logger.warning(f"Collection '{old_name}' not found, skipping")
                return 0

            if total_points == 0:
                logger.info(f"No memories to migrate from '{old_name}'")
                return 0

            # Create new collection
            if not self.create_v3_2_collection(new_name):
                return 0

            # Migrate in batches
            migrated = 0
            batch_size = 100
            offset = None

            while True:
                # Scroll through old collection
                records, next_offset = self.client.scroll(
                    collection_name=old_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True
                )

                if not records:
                    break

                # Transform and insert into new collection
                points_to_insert = []
                for record in records:
                    # Update metadata for V3.2
                    payload = record.payload.copy()

                    # Update role names if present
                    if "role" in payload:
                        role_mapping = {
                            "backend-dev": "backend",
                            "frontend-dev": "frontend",
                            "financial-engineer": "quant",
                            "coder": "universal"
                        }
                        payload["role"] = role_mapping.get(payload["role"], payload["role"])

                    # Add migration metadata
                    payload["migrated_from"] = old_name
                    payload["migration_date"] = datetime.now().isoformat()

                    # Create new point
                    points_to_insert.append(
                        models.PointStruct(
                            id=record.id,
                            vector=record.vector,
                            payload=payload
                        )
                    )

                # Insert batch into new collection
                self.client.upsert(
                    collection_name=new_name,
                    points=points_to_insert
                )

                migrated += len(records)
                logger.info(f"Migrated {migrated}/{total_points} memories")

                # Check if done
                if next_offset is None:
                    break
                offset = next_offset

            logger.info(f"✅ Migrated {migrated} memories from '{old_name}' to '{new_name}'")
            self.migration_report["collections_migrated"].append(f"{old_name} -> {new_name}")
            self.migration_report["memories_migrated"] += migrated
            return migrated

        except Exception as e:
            logger.error(f"Failed to migrate '{old_name}': {e}")
            self.migration_report["errors"].append(f"Migrate {old_name}: {str(e)}")
            return 0

    def backup_collection(self, collection_name: str) -> bool:
        """Create a backup of collection before migration"""
        try:
            backup_name = f"{collection_name}-backup-v3"

            # Check if backup already exists
            try:
                self.client.get_collection(backup_name)
                logger.info(f"Backup '{backup_name}' already exists")
                return True
            except:
                pass

            # Get original collection info
            try:
                original = self.client.get_collection(collection_name)
            except:
                logger.warning(f"Collection '{collection_name}' not found for backup")
                return False

            # Create backup collection
            self.client.create_collection(
                collection_name=backup_name,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE
                )
            )

            # Copy all points
            offset = None
            copied = 0

            while True:
                records, next_offset = self.client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True
                )

                if not records:
                    break

                self.client.upsert(
                    collection_name=backup_name,
                    points=records
                )

                copied += len(records)

                if next_offset is None:
                    break
                offset = next_offset

            logger.info(f"✅ Backed up {copied} memories to '{backup_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to backup '{collection_name}': {e}")
            return False

    def migrate_project_collections(self):
        """Migrate project collections (keep same names)"""
        existing = self.get_existing_collections()

        for collection in existing:
            if collection.startswith("proj-"):
                # Project collections keep their names but get updated metadata
                logger.info(f"Updating project collection: {collection}")
                try:
                    # Just update metadata for existing memories
                    offset = None
                    updated = 0

                    while True:
                        records, next_offset = self.client.scroll(
                            collection_name=collection,
                            limit=100,
                            offset=offset,
                            with_payload=True,
                            with_vectors=False
                        )

                        if not records:
                            break

                        # Update metadata
                        for record in records:
                            payload = record.payload.copy()
                            payload["v3_2_migration"] = datetime.now().isoformat()

                            self.client.set_payload(
                                collection_name=collection,
                                payload=payload,
                                points=[record.id]
                            )

                        updated += len(records)

                        if next_offset is None:
                            break
                        offset = next_offset

                    logger.info(f"Updated {updated} memories in '{collection}'")
                    self.migration_report["collections_migrated"].append(f"{collection} (updated)")

                except Exception as e:
                    logger.error(f"Failed to update project collection '{collection}': {e}")
                    self.migration_report["errors"].append(f"Update {collection}: {str(e)}")

    def run_migration(self, backup: bool = True):
        """Run the complete migration"""
        logger.info("=" * 60)
        logger.info("Starting V3 to V3.2 Migration")
        logger.info("=" * 60)

        # Step 1: Backup existing collections
        if backup:
            logger.info("\n📦 Creating backups...")
            for old_name in COLLECTION_MAPPING.keys():
                self.backup_collection(old_name)

        # Step 2: Migrate global collections
        logger.info("\n🔄 Migrating global collections...")
        for old_name, new_name in COLLECTION_MAPPING.items():
            self.migrate_collection(old_name, new_name)

        # Step 3: Create new V3.2 collections
        logger.info("\n✨ Creating new V3.2 collections...")
        for collection in NEW_COLLECTIONS:
            self.create_v3_2_collection(collection)

        # Step 4: Update project collections
        logger.info("\n📝 Updating project collections...")
        self.migrate_project_collections()

        # Step 5: Print migration report
        self.print_report()

    def print_report(self):
        """Print migration report"""
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION REPORT")
        logger.info("=" * 60)

        logger.info(f"\n✅ Collections Migrated: {len(self.migration_report['collections_migrated'])}")
        for item in self.migration_report["collections_migrated"]:
            logger.info(f"   - {item}")

        logger.info(f"\n✨ Collections Created: {len(self.migration_report['collections_created'])}")
        for item in self.migration_report["collections_created"]:
            logger.info(f"   - {item}")

        logger.info(f"\n📊 Total Memories Migrated: {self.migration_report['memories_migrated']}")

        if self.migration_report["errors"]:
            logger.error(f"\n❌ Errors: {len(self.migration_report['errors'])}")
            for error in self.migration_report["errors"]:
                logger.error(f"   - {error}")
        else:
            logger.info("\n✅ No errors encountered")

        logger.info("\n" + "=" * 60)

def main():
    """Main migration function"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate V3 to V3.2 memory system")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups (not recommended)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        manager = MigrationManager()
        existing = manager.get_existing_collections()

        logger.info("\nExisting collections:")
        for collection in existing:
            logger.info(f"  - {collection}")

        logger.info("\nPlanned migrations:")
        for old, new in COLLECTION_MAPPING.items():
            if old in existing:
                info = manager.client.get_collection(old)
                logger.info(f"  {old} -> {new} ({info.points_count} memories)")

        logger.info("\nNew collections to create:")
        for collection in NEW_COLLECTIONS:
            logger.info(f"  - {collection}")
    else:
        # Run actual migration
        manager = MigrationManager()
        manager.run_migration(backup=not args.no_backup)

        logger.info("\n🎉 Migration complete!")
        logger.info("Next steps:")
        logger.info("1. Test the new collections with V3.2 skills")
        logger.info("2. Update MCP server to use qdrant_memory_mcp_server_v2.py")
        logger.info("3. Install V3.2 skills to ~/.claude/skills/")
        logger.info("4. Restart Claude Code")

if __name__ == "__main__":
    main()