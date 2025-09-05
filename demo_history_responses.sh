#!/bin/bash

# Demo script to show how the context system responds to different history questions
# Make sure the FastMCP server is running on localhost:8000

echo "=== Context System - History Question Responses Demo ==="
echo ""

# Test 1: What did I do last?
echo "1. Testing: 'What did I do last?'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what did I do last?", "session_id": "demo_history_1"}' | jq -r '.model_summary'
echo ""

# Test 2: What was my previous project?
echo "2. Testing: 'What was my previous project?'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what was my previous project?", "session_id": "demo_history_2"}' | jq -r '.model_summary'
echo ""

# Test 3: Show me my recent work
echo "3. Testing: 'Show me my recent work'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "show me my recent work", "session_id": "demo_history_3"}' | jq -r '.model_summary'
echo ""

# Test 4: What have I been working on?
echo "4. Testing: 'What have I been working on?'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what have I been working on?", "session_id": "demo_history_4"}' | jq -r '.model_summary'
echo ""

# Test 5: Show me my conversation history
echo "5. Testing: 'Show me my conversation history'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "show me my conversation history", "session_id": "demo_history_5"}' | jq -r '.model_summary'
echo ""

# Test 6: What repositories have I worked with?
echo "6. Testing: 'What repositories have I worked with?'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what repositories have I worked with?", "session_id": "demo_history_6"}' | jq -r '.model_summary'
echo ""

# Test 7: What branches are available in my current project?
echo "7. Testing: 'What branches are available in my current project?'"
curl -s -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what branches are available in my current project?", "session_id": "demo_history_7"}' | jq -r '.model_summary'
echo ""

echo "=== Demo Complete ==="
echo ""
echo "The context system provides detailed responses based on:"
echo "- Recent actions (last 10 tool calls)"
echo "- Conversation history (last 5 conversations)"
echo "- Current repository and branch information"
echo "- Recent GitHub and Jira activities"
echo "- Cross-session persistence"
