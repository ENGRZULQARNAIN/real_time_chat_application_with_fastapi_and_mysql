#!/bin/bash

# Script for running database migrations
# Usage:
#   ./scripts/run_migrations.sh [command]
#
# Commands:
#   init      - Initialize a new migration repository
#   create    - Create a new migration (requires a message)
#   upgrade   - Upgrade to the latest migration
#   downgrade - Downgrade to the previous migration
#   history   - Show migration history
#   current   - Show current migration
#   test      - Test migrations by downgrading and upgrading

set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if a command argument was provided
if [ $# -eq 0 ]; then
    echo "Error: No command provided."
    echo "Usage: ./scripts/run_migrations.sh [command] [message]"
    echo "Commands: init, create, upgrade, downgrade, history, current, test"
    exit 1
fi

# Get the command argument
COMMAND=$1

case $COMMAND in
    init)
        # Initialize a new Alembic migration environment
        echo "Initializing new Alembic migration environment..."
        python -m alembic init app/alembic
        ;;
    
    create)
        # Check if a message was provided
        if [ $# -lt 2 ]; then
            echo "Error: Migration message required."
            echo "Usage: ./scripts/run_migrations.sh create 'migration message'"
            exit 1
        fi

        # Create a new migration with the provided message
        MESSAGE="${@:2}"
        echo "Creating new migration: $MESSAGE"
        python -m alembic revision --autogenerate -m "$MESSAGE"
        ;;
    
    upgrade)
        # Upgrade to the latest or specified revision
        TARGET="head"
        if [ $# -gt 1 ]; then
            TARGET=$2
        fi
        echo "Upgrading database to $TARGET..."
        python -m alembic upgrade $TARGET
        ;;
    
    downgrade)
        # Downgrade to the previous or specified revision
        TARGET="-1"
        if [ $# -gt 1 ]; then
            TARGET=$2
        fi
        echo "Downgrading database to $TARGET..."
        python -m alembic downgrade $TARGET
        ;;
    
    history)
        # Show migration history
        echo "Migration history:"
        python -m alembic history
        ;;
    
    current)
        # Show current migration
        echo "Current migration:"
        python -m alembic current
        ;;
    
    test)
        # Test migrations by downgrading and upgrading
        echo "Testing migrations..."
        echo "Current version:"
        python -m alembic current
        
        echo "Downgrading one version..."
        python -m alembic downgrade -1
        
        echo "Upgrading back to latest..."
        python -m alembic upgrade head
        
        echo "Migration test completed."
        ;;
    
    *)
        echo "Error: Unknown command '$COMMAND'."
        echo "Available commands: init, create, upgrade, downgrade, history, current, test"
        exit 1
        ;;
esac

echo "Migration command '$COMMAND' completed successfully." 