# Web console persistence migration guide

This guide explains how to migrate from the old browser-only state model
(`localStorage`) to the new server-backed persistence model in the ANIMAtiZE
Director Console. Use this guide if you are upgrading from a build that stored
settings and run history only in the current browser profile.

## What changed

The console now persists session state and user data on the backend.
Configuration is no longer tied only to one browser tab or one machine.

- Auth and session management are stored server-side.
- Settings are versioned and restorable.
- Generation runs are persisted and can be synced across devices.
- Provider API keys are encrypted at rest.
- Backup and restore are available from the Settings view.

## Legacy versus new data model

Legacy builds stored two keys in browser `localStorage`:

- `animatize_ui_settings_v2`
- `animatize_ui_runs_v2`

The new runtime stores data in SQLite through backend APIs:

- `GET/PUT /api/settings`
- `GET /api/settings/history`
- `POST /api/settings/history/{history_id}/restore`
- `GET /api/runs`
- `GET /api/settings/backup`
- `POST /api/settings/restore`

## Migration paths

You can migrate using one of the following paths, depending on what data you
have.

### Path 1: in-app backup/restore (recommended)

Use this path if you already use the new runtime and want to move data between
environments.

1. In the source environment, open **Settings**.
2. In **Data Sync, Export & Restore**, click **Export backup**.
3. In the target environment, open **Settings**.
4. In **Data Sync, Export & Restore**, click **Import backup**.
5. Verify runs in **Library** and settings in **Settings Console**.

### Path 2: import legacy localStorage export

Use this path when you are upgrading from an old build.

1. Open the old UI in your browser.
2. Export your local storage keys into one JSON file with:
   `animatize_ui_settings_v2` and `animatize_ui_runs_v2`.
3. Start the new runtime.
4. Open **Settings** and click **Import backup**.
5. Select the JSON file from step 2.
6. Verify that:
   - theme and preferences are restored,
   - run history appears in **Library**.

> **Note:** The restore endpoint accepts both the new backup format and the
> legacy key format.

## Required environment variables

Set these values before production rollout:

- `ANIMATIZE_SECRET_KEY` for encryption key derivation.
- `GOOGLE_CLIENT_ID` for Google sign-in.
- `ANIMATIZE_WEB_DB_PATH` to control SQLite location.

## Post-migration validation checklist

Run these checks after migration to confirm integrity:

1. Call `GET /api/settings` and confirm non-default values when expected.
2. Call `GET /api/settings/history` and confirm version entries exist.
3. Call `GET /api/runs` and confirm imported runs are present.
4. Call `GET /api/providers` and confirm provider availability is correct.
5. Restart the app and verify settings and runs persist.

## Rollback and recovery

If migration data looks incorrect, restore from the latest backup file and
retry import. If you need a clean state for one profile, clear runs from the
UI and save baseline settings again.

## Next steps

After migration, add this guide to your operational runbook and include backup
export in your regular environment change process.
