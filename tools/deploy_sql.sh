#!/usr/bin/env bash
# tools/deploy_sql.sh — Execute SQL files with optional table backup
#
# Usage:
#   export DATABASE_URL='postgresql://postgres:...@db.xxx.supabase.co:5432/postgres'
#
#   bash tools/deploy_sql.sh \
#     --backup-table public.properties \
#     backend/migrations/004_add_property_fields.sql \
#     backend/seeds/002_seed_property_fields.sql
#
# Flags:
#   --backup-table <schema.table>   Dump this table before executing. Repeatable.
#   --backup-dir <dir>              Backup destination. Default: ./sql_backups
#   --yes                           Skip confirmation prompt.

set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BOLD='\033[1m'; RESET='\033[0m'
err()  { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
info() { echo -e "${GREEN}[INFO]${RESET}  $*"; }

# ── Parse arguments ────────────────────────────────────────────────────────────
backup_tables=()
backup_dir="./sql_backups"
sql_files=()
auto_yes=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backup-table) [[ -z "${2:-}" ]] && { err "--backup-table requires a value"; exit 1; }
                        backup_tables+=("$2"); shift 2 ;;
        --backup-dir)   [[ -z "${2:-}" ]] && { err "--backup-dir requires a value"; exit 1; }
                        backup_dir="$2"; shift 2 ;;
        --yes)          auto_yes=true; shift ;;
        -*)             err "Unknown flag: $1"; exit 1 ;;
        *)              sql_files+=("$1"); shift ;;
    esac
done

# ── Validate ──────────────────────────────────────────────────────────────────
[[ ${#sql_files[@]} -eq 0 ]] && {
    err "No SQL files specified."
    echo "Usage: bash tools/deploy_sql.sh [--backup-table schema.table] file1.sql ..."
    exit 1
}

[[ -z "${DATABASE_URL:-}" ]] && {
    err "DATABASE_URL is not set."
    echo "  export DATABASE_URL='postgresql://postgres:PASSWORD@db.REF.supabase.co:5432/postgres'"
    exit 1
}

command -v psql &>/dev/null || { err "psql not found. Install: apt-get install -y postgresql-client"; exit 1; }

[[ ${#backup_tables[@]} -gt 0 ]] && ! command -v pg_dump &>/dev/null && {
    err "pg_dump not found. Install: apt-get install -y postgresql-client"
    exit 1
}

for f in "${sql_files[@]}"; do
    [[ -f "$f" ]] || { err "File not found: $f"; exit 1; }
done

# ── Connectivity check ────────────────────────────────────────────────────────
info "Checking database connection..."
psql "$DATABASE_URL" -c "SELECT 1" -q --no-psqlrc > /dev/null || {
    err "Cannot connect to database. Check DATABASE_URL."
    exit 1
}
info "Connection OK."
echo ""

# ── Plan summary ──────────────────────────────────────────────────────────────
echo -e "${BOLD}SQL files:${RESET}"
for f in "${sql_files[@]}"; do echo "  $f"; done
echo ""

if [[ ${#backup_tables[@]} -gt 0 ]]; then
    echo -e "${BOLD}Tables to back up first:${RESET}"
    for t in "${backup_tables[@]}"; do echo "  $t"; done
    echo ""
fi

# ── Confirm ───────────────────────────────────────────────────────────────────
if ! $auto_yes; then
    read -r -p "Proceed? [y/N] " confirm
    echo ""
    [[ "$confirm" =~ ^[Yy]$ ]] || { warn "Aborted."; exit 0; }
fi

# ── Backup ────────────────────────────────────────────────────────────────────
if [[ ${#backup_tables[@]} -gt 0 ]]; then
    mkdir -p "$backup_dir"
    timestamp=$(date +%Y%m%d_%H%M%S)

    for tbl in "${backup_tables[@]}"; do
        safe_name="${tbl//[^a-zA-Z0-9_]/_}"
        backup_file="${backup_dir}/${safe_name}_${timestamp}.sql"
        info "Backing up $tbl → $backup_file"
        pg_dump "$DATABASE_URL" --no-owner --no-privileges -t "$tbl" > "$backup_file"
        info "  $(wc -c < "$backup_file") bytes written"
    done
    echo ""
fi

# ── Execute ───────────────────────────────────────────────────────────────────
for f in "${sql_files[@]}"; do
    info "Running: $f"
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
    info "  OK"
    echo ""
done

info "All done."
[[ ${#backup_tables[@]} -gt 0 ]] && info "Backups saved in: $backup_dir"
