#!/usr/bin/env bash
#
# clean.sh — stop the stack and wipe EVERYTHING it created
#            (containers, images, networks, volumes).
#
# Run from the directory that holds your docker-compose.yml.
# You WILL lose any data stored in the volumes.
#

set -euo pipefail

# Always work from this file’s directory so the relative compose file resolves.
cd "$(dirname "$0")"

echo "🛑  Bringing down docker compose stack and deleting all artifacts…"

# --rmi all      : delete every image referenced or built by the compose file
# --volumes (-v) : delete named AND anonymous volumes declared by the file
# --remove-orphans: delete containers left over from old compose runs
docker compose down --rmi all --volumes --remove-orphans

# Optional: reclaim any other dangling resources on your machine.
# Comment out any lines you don’t want.
docker image  prune -af   # dangling & unused images
docker volume prune -f    # dangling volumes
docker network prune -f   # dangling networks

echo "✅  Cleanup complete."