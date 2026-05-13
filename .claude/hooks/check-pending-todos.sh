#!/bin/bash

TODOS_FILE=".cerebro/.pending-todos"

if [ -f "$TODOS_FILE" ] && [ -s "$TODOS_FILE" ]; then
    echo ""
    echo "[SYSTEM REMINDER - TODO CONTINUATION]"
    echo ""
    echo "You have incomplete todos! Complete ALL before responding:"
    echo ""
    while IFS= read -r line; do
        echo "  - [ ] $line"
    done < "$TODOS_FILE"
    echo ""
    echo "DO NOT respond until all todos are marked completed and removed from .cerebro/.pending-todos"
    echo ""
    exit 1
fi

exit 0
