# PowerShell script for running database migrations
# Usage:
#   .\scripts\run_migrations.ps1 [command]
#
# Commands:
#   init      - Initialize a new migration repository
#   create    - Create a new migration (requires a message)
#   upgrade   - Upgrade to the latest migration
#   downgrade - Downgrade to the previous migration
#   history   - Show migration history
#   current   - Show current migration
#   test      - Test migrations by downgrading and upgrading

# Set the error action preference to stop on error
$ErrorActionPreference = "Stop"

# Change to the project root directory
Set-Location (Split-Path -Parent $PSScriptRoot)

# Check if a command argument was provided
if ($args.Count -eq 0) {
    Write-Error "Error: No command provided."
    Write-Host "Usage: .\scripts\run_migrations.ps1 [command] [message]"
    Write-Host "Commands: init, create, upgrade, downgrade, history, current, test"
    exit 1
}

# Get the command argument
$COMMAND = $args[0]

switch ($COMMAND) {
    "init" {
        # Initialize a new Alembic migration environment
        Write-Host "Initializing new Alembic migration environment..."
        python -m alembic init app/alembic
    }
    
    "create" {
        # Check if a message was provided
        if ($args.Count -lt 2) {
            Write-Error "Error: Migration message required."
            Write-Host "Usage: .\scripts\run_migrations.ps1 create 'migration message'"
            exit 1
        }

        # Create a new migration with the provided message
        $MESSAGE = $args[1..($args.Count-1)] -join " "
        Write-Host "Creating new migration: $MESSAGE"
        python -m alembic revision --autogenerate -m "$MESSAGE"
    }
    
    "upgrade" {
        # Upgrade to the latest or specified revision
        $TARGET = "head"
        if ($args.Count -gt 1) {
            $TARGET = $args[1]
        }
        Write-Host "Upgrading database to $TARGET..."
        python -m alembic upgrade $TARGET
    }
    
    "downgrade" {
        # Downgrade to the previous or specified revision
        $TARGET = "-1"
        if ($args.Count -gt 1) {
            $TARGET = $args[1]
        }
        Write-Host "Downgrading database to $TARGET..."
        python -m alembic downgrade $TARGET
    }
    
    "history" {
        # Show migration history
        Write-Host "Migration history:"
        python -m alembic history
    }
    
    "current" {
        # Show current migration
        Write-Host "Current migration:"
        python -m alembic current
    }
    
    "test" {
        # Test migrations by downgrading and upgrading
        Write-Host "Testing migrations..."
        Write-Host "Current version:"
        python -m alembic current
        
        Write-Host "Downgrading one version..."
        python -m alembic downgrade -1
        
        Write-Host "Upgrading back to latest..."
        python -m alembic upgrade head
        
        Write-Host "Migration test completed."
    }
    
    default {
        Write-Error "Error: Unknown command '$COMMAND'."
        Write-Host "Available commands: init, create, upgrade, downgrade, history, current, test"
        exit 1
    }
}

Write-Host "Migration command '$COMMAND' completed successfully." 