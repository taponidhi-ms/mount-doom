#!/bin/bash
# Authentication Monitor Script for Mount Doom Backend
# Checks backend logs every 5 minutes for auth errors

BACKEND_LOG="C:/Users/ttulsi/AppData/Local/Temp/claude/C--Users-ttulsi-GithubProjects-mount-doom/tasks/b7079d9.output"
CHECK_INTERVAL=300  # 5 minutes in seconds

echo "=== Authentication Monitor Started ==="
echo "Monitoring backend logs for authentication errors..."
echo "Checking every 5 minutes"
echo "Log file: $BACKEND_LOG"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Check if log file exists
    if [ ! -f "$BACKEND_LOG" ]; then
        echo "[$TIMESTAMP] WARNING: Backend log file not found. Waiting..."
        sleep $CHECK_INTERVAL
        continue
    fi

    # Get last 100 lines and check for auth errors
    RECENT_LOGS=$(tail -100 "$BACKEND_LOG" 2>/dev/null)

    # Check for authentication error patterns
    AUTH_ERROR=$(echo "$RECENT_LOGS" | grep -iE "(DefaultAzureCredential failed|ClientAuthenticationError|Authentication failed|Token expired|401|403|Unauthorized|AADSTS)" | tail -5)

    if [ ! -z "$AUTH_ERROR" ]; then
        echo ""
        echo "[$TIMESTAMP] ⚠️  AUTHENTICATION ERROR DETECTED!"
        echo "----------------------------------------"
        echo "$AUTH_ERROR"
        echo "----------------------------------------"
        echo ""
        echo "Running: az account get-access-token"

        # Try to get access token
        TOKEN_OUTPUT=$(az account get-access-token 2>&1)
        TOKEN_EXIT_CODE=$?

        if [ $TOKEN_EXIT_CODE -eq 0 ]; then
            echo "✅ Azure CLI authentication is valid"
            echo "Token retrieved successfully. If backend still has issues, check:"
            echo "  - AZURE_AI_PROJECT_CONNECTION_STRING in .env"
            echo "  - Azure subscription permissions"
            echo "  - Service principal configuration"
        else
            echo "❌ Azure CLI authentication failed!"
            echo "$TOKEN_OUTPUT"
            echo ""
            echo "ACTION REQUIRED: Please run 'az login' to re-authenticate"
        fi
        echo ""
    else
        echo "[$TIMESTAMP] ✓ No authentication errors detected"
    fi

    sleep $CHECK_INTERVAL
done
