#!/bin/bash

echo "🧪 AdGen Studio Backend Test Runner"
echo "=================================="

# Check if server is running
echo "🔍 Checking if backend server is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server is running"
else
    echo "❌ Backend server is not running"
    echo "💡 Please start the server first:"
    echo "   cd backend && python run.py"
    echo ""
    read -p "Start server automatically? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Starting backend server..."
        python run.py &
        SERVER_PID=$!
        echo "⏳ Waiting for server to start..."
        sleep 5

        # Check if server started successfully
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ Server started successfully"
        else
            echo "❌ Failed to start server"
            exit 1
        fi
    else
        echo "❌ Cannot run tests without server"
        exit 1
    fi
fi

echo ""
echo "🧪 Running API tests..."
echo "========================"

# Run the tests
python test_api.py

TEST_EXIT_CODE=$?

# Clean up server if we started it
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    echo "🛑 Stopping backend server..."
    kill $SERVER_PID
fi

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed!"
else
    echo "⚠️  Some tests failed. Check the output above."
fi

exit $TEST_EXIT_CODE