#!/bin/bash
# Database Setup Validation Script
# Tests that PostgreSQL is properly configured and accessible

set -e  # Exit on any error

echo "🔍 Validating PostgreSQL Database Setup..."
echo

# Test 1: Check docker-compose.yml exists
echo "✓ Test 1: Checking docker-compose.yml exists..."
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ FAIL: docker-compose.yml not found"
    exit 1
fi
echo "  ✅ PASS: docker-compose.yml found"
echo

# Test 2: Check .env.example exists
echo "✓ Test 2: Checking .env.example exists..."
if [ ! -f ".env.example" ]; then
    echo "❌ FAIL: .env.example not found"
    exit 1
fi
echo "  ✅ PASS: .env.example found"
echo

# Test 3: Start PostgreSQL container
echo "✓ Test 3: Starting PostgreSQL container..."
docker-compose up -d postgres
sleep 5  # Give container time to initialize
echo "  ✅ PASS: Container started"
echo

# Test 4: Check container is running
echo "✓ Test 4: Checking container status..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ FAIL: PostgreSQL container is not running"
    docker-compose logs postgres
    exit 1
fi
echo "  ✅ PASS: Container is running"
echo

# Test 5: Wait for health check to pass
echo "✓ Test 5: Waiting for health check..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose ps postgres | grep -q "healthy"; then
        echo "  ✅ PASS: Health check passed"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ FAIL: Health check did not pass after 30 attempts"
        docker-compose logs postgres
        exit 1
    fi
    sleep 1
done
echo

# Test 6: Test database connectivity
echo "✓ Test 6: Testing database connectivity..."
if ! docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ FAIL: Cannot connect to database"
    docker-compose logs postgres
    exit 1
fi
echo "  ✅ PASS: Database connection successful"
echo

# Test 7: Verify database exists
echo "✓ Test 7: Verifying ai_interviewer_db exists..."
if ! docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "\l" | grep -q "ai_interviewer_db"; then
    echo "❌ FAIL: ai_interviewer_db database not found"
    exit 1
fi
echo "  ✅ PASS: Database exists"
echo

# Test 8: Test data persistence
echo "✓ Test 8: Testing data persistence..."
docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "CREATE TABLE IF NOT EXISTS test_persistence (id SERIAL PRIMARY KEY, data TEXT);" > /dev/null 2>&1
docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "INSERT INTO test_persistence (data) VALUES ('test data');" > /dev/null 2>&1

# Restart container
echo "  Restarting container to test persistence..."
docker-compose restart postgres
sleep 5

# Wait for health check again
attempt=0
while [ $attempt -lt 30 ]; do
    if docker-compose ps postgres | grep -q "healthy"; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

# Check if data persists
if ! docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "SELECT * FROM test_persistence WHERE data='test data';" | grep -q "test data"; then
    echo "❌ FAIL: Data did not persist after restart"
    exit 1
fi

# Cleanup test table
docker-compose exec -T postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "DROP TABLE test_persistence;" > /dev/null 2>&1
echo "  ✅ PASS: Data persistence verified"
echo

# Test 9: Verify volume exists
echo "✓ Test 9: Checking PostgreSQL volume..."
if ! docker volume ls | grep -q "postgres_data"; then
    echo "❌ FAIL: postgres_data volume not found"
    exit 1
fi
echo "  ✅ PASS: Volume exists"
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL TESTS PASSED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "PostgreSQL database is properly configured and ready for use."
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: ai_interviewer_db"
echo "  User: ai_interviewer_user"
echo

exit 0
