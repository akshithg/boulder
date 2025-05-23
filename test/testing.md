# Test Types in Boulder

## 1. Unit Tests

- **Location:** `*_test.go` files throughout the codebase
- **Framework:** Go's built-in testing framework
- **Execution:** `go test -p 1 ./...` (serial execution required due to shared database state)
- **Race Detection:** Available with `-race` flag
- **Purpose:** Test individual functions and components in isolation

## 2. Integration Tests

- **Location:** `test/integration-test.py` and `test/integration/` directory
- **Framework:** Python-based test framework with Go integration tests
- **Types:**
  - **Chisel tests:** Python-based end-to-end ACME protocol tests (`v2_integration.py`)
  - **Go integration tests:** Go tests with `-tags integration` in `test/integration/`
- **Execution:** `python3 test/integration-test.py --chisel --gotest`
- **Purpose:** Test complete ACME workflows and inter-service communication

## 3. Linting Tests

- **golangci-lint:** Go code quality and style checking
- **staticcheck:** Advanced Go static analysis
- **Python linting:** `python3 test/grafana/lint.py` for Python code
- **typos:** Spell checking across the codebase
- **Config formatting:** `./test/format-configs.py` for JSON config consistency

## 4. Start/Smoke Tests

- **Purpose:** Verify that `./start.py` and `docker compose up` work correctly
- **Test:** Starts all services and checks if Boulder comes up within 115 seconds
- **Health checks:** Verifies ACME directory endpoint is accessible

## 5. Generate Tests

- **Purpose:** Ensure all generated code can be re-generated with current tools
- **Process:** Runs `go generate ./...` and verifies no files were modified
- **Dependencies:** Requires `go install` for certain packages before generation

## 6. Load Balancing Tests

- **Function:** `check_balance()` in integration tests
- **Purpose:** Verify gRPC load balancing across backend services
- **Method:** Checks metrics endpoints to ensure all backends handle requests

## 7. Certificate Checker Tests

- **Tool:** `cert-checker` binary
- **Purpose:** Validate issued certificates meet requirements
- **Execution:** Runs as part of integration test suite

## 8. Time-Travel Tests

- **Purpose:** Test certificate lifecycle and expiration scenarios
- **Method:** Uses fake clock to simulate different time periods:
  - 6 months ago setup
  - 20 days ago setup
  - Current time tests
- **Controlled by:** `FAKECLOCK` environment variable

## 9. Service Health Tests

- **Built into:** `startservers.py` infrastructure
- **Purpose:** Continuous monitoring that all services remain healthy
- **Method:** Polls debug ports and gRPC health endpoints

## 10. Database Migration Tests

- **Integration:** Part of feature flag testing
- **Purpose:** Ensure database schema changes work before/during/after migration
- **Method:** Tests different model struct versions with feature flags

## 11. gRPC Communication Tests

- **Embedded in:** Integration and unit tests
- **Purpose:** Test inter-service gRPC communication

## 12. Challenge Response Tests

- **Infrastructure:** `challtestsrv` (Challenge Test Server)
- **Purpose:** Mock domain validation challenges (HTTP-01, DNS-01, TLS-ALPN-01)
- **Ports:** Multiple ports for different challenge types and interfaces

## 13. Certificate Transparency Tests

- **Infrastructure:** `ct-test-srv`
- **Purpose:** Mock Certificate Transparency log submission
- **Integration:** Tests Publisher component functionality

## 14. Email/Notification Tests

- **Infrastructure:** `mail-test-srv`, `pardot-test-srv`
- **Purpose:** Test email notifications and CRM integration
- **Components:** Email exporter, Pardot integration

---

## Test Execution Patterns

- **Serial Execution:** Unit tests run with `-p=1` due to shared database state that could cause race conditions.
- **Filter Support:** Both unit and integration tests support regex filtering for running specific test subsets.
- **Race Detection:** Available for both unit and integration tests when enabled with  `--enable-race-detection` flag.
- **Dependency Management:** Services start in topologically sorted order based on dependencies defined in `startservers.py`.
- **Coverage Collection:** Available across all test types with `--coverage` and `--coverage_dir=<dir>` flags. (NEW)
