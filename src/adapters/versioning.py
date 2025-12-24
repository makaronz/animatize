from typing import Dict, Any, Callable, List
from .contracts import (
    SchemaVersion,
    VersionMigration,
)
import logging

logger = logging.getLogger(__name__)


class VersionManager:
    def __init__(self):
        self.migrations: Dict[tuple, VersionMigration] = {}
        self._register_default_migrations()

    def _register_default_migrations(self):
        self.register_migration(
            SchemaVersion.V1_0,
            SchemaVersion.V1_1,
            self._migrate_v1_0_to_v1_1,
            backward_compatible=True,
        )

        self.register_migration(
            SchemaVersion.V1_1,
            SchemaVersion.V2_0,
            self._migrate_v1_1_to_v2_0,
            backward_compatible=False,
        )

    def register_migration(
        self,
        from_version: SchemaVersion,
        to_version: SchemaVersion,
        migration_fn: Callable,
        backward_compatible: bool = True,
    ):
        key = (from_version, to_version)
        migration = VersionMigration(
            from_version=from_version,
            to_version=to_version,
            migration_fn=migration_fn,
            backward_compatible=backward_compatible,
        )
        self.migrations[key] = migration
        logger.info(f"Registered migration: {from_version.value} -> {to_version.value}")

    def migrate_request(
        self,
        request_data: Dict[str, Any],
        target_version: SchemaVersion,
    ) -> Dict[str, Any]:
        current_version = SchemaVersion(request_data.get("schema_version", "1.0"))

        if current_version == target_version:
            return request_data

        migration_path = self._find_migration_path(current_version, target_version)

        if not migration_path:
            raise ValueError(
                f"No migration path found from {current_version.value} "
                f"to {target_version.value}"
            )

        migrated_data = request_data.copy()

        for from_ver, to_ver in migration_path:
            migration = self.migrations[(from_ver, to_ver)]
            migrated_data = migration.migration_fn(migrated_data)
            migrated_data["schema_version"] = to_ver.value
            logger.debug(f"Migrated request from {from_ver.value} to {to_ver.value}")

        return migrated_data

    def migrate_response(
        self,
        response_data: Dict[str, Any],
        target_version: SchemaVersion,
    ) -> Dict[str, Any]:
        return self.migrate_request(response_data, target_version)

    def _find_migration_path(
        self,
        from_version: SchemaVersion,
        to_version: SchemaVersion,
    ) -> List[tuple]:
        if from_version == to_version:
            return []

        versions = [SchemaVersion.V1_0, SchemaVersion.V1_1, SchemaVersion.V2_0]

        try:
            from_idx = versions.index(from_version)
            to_idx = versions.index(to_version)
        except ValueError:
            return []

        if from_idx < to_idx:
            path = [(versions[i], versions[i + 1]) for i in range(from_idx, to_idx)]
        else:
            path = [(versions[i], versions[i - 1]) for i in range(from_idx, to_idx, -1)]

        for step in path:
            if step not in self.migrations:
                return []

        return path

    def _migrate_v1_0_to_v1_1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        migrated = data.copy()

        if "metadata" not in migrated:
            migrated["metadata"] = {}

        if "retry_config" not in migrated:
            migrated["retry_config"] = {
                "max_retries": 3,
                "retry_delay": 1.0,
            }

        if "result" in migrated and isinstance(migrated["result"], dict):
            if "output_url" in migrated["result"]:
                migrated["result"]["urls"] = [migrated["result"]["output_url"]]

        return migrated

    def _migrate_v1_1_to_v2_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        migrated = data.copy()

        if "provider" in migrated and isinstance(migrated["provider"], str):
            migrated["provider_info"] = {
                "name": migrated["provider"],
                "version": "unknown",
                "region": "unknown",
            }

        if "error" in migrated and migrated["error"]:
            error = migrated["error"]
            if isinstance(error, dict):
                migrated["error"] = {
                    "code": error.get("code", "unknown_error"),
                    "message": error.get("message", ""),
                    "retryable": error.get("retryable", False),
                    "provider": error.get("provider", "unknown"),
                    "details": error.get("details", {}),
                    "timestamp": error.get("timestamp"),
                    "retry_after": error.get("retry_after"),
                    "correlation_id": data.get("request_id"),
                }

        if "parameters" in migrated and isinstance(migrated["parameters"], dict):
            params = migrated["parameters"]
            migrated["generation_config"] = {
                "quality": params.get("quality", "standard"),
                "safety_settings": params.get("safety_settings", {}),
                "advanced_options": {
                    k: v for k, v in params.items() if k not in ["quality", "safety_settings"]
                },
            }

        return migrated

    def is_compatible(
        self,
        from_version: SchemaVersion,
        to_version: SchemaVersion,
    ) -> bool:
        path = self._find_migration_path(from_version, to_version)

        if not path:
            return from_version == to_version

        for step in path:
            migration = self.migrations.get(step)
            if not migration or not migration.backward_compatible:
                return False

        return True

    def get_latest_version(self) -> SchemaVersion:
        return SchemaVersion.V2_0

    def get_supported_versions(self) -> List[SchemaVersion]:
        return [SchemaVersion.V1_0, SchemaVersion.V1_1, SchemaVersion.V2_0]
