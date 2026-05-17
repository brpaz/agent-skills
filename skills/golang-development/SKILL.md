---
name: golang-development
description: "Go programming language best practices, patterns, and idioms. USE WHEN writing, refactoring, or debugging Go code. Covers project structure, error handling, concurrency, testing, performance optimization, and common pitfalls. Essential for building production-ready Go applications."
---

# Go (Golang) - Best Practices and Patterns

Use this skill when writing, reviewing, or debugging Go code. Covers idiomatic Go patterns, project structure, concurrency, testing, and production-ready practices.

## Go Philosophy

**Core principles:**
- Simplicity over cleverness
- Explicit over implicit
- Composition over inheritance
- Clear is better than clever
- Errors are values
- Concurrency is not parallelism

**Key idioms:**
- "Don't communicate by sharing memory; share memory by communicating"
- "A little copying is better than a little dependency"
- "The bigger the interface, the weaker the abstraction"
- "Make the zero value useful"
- "Accept interfaces, return structs"

## Project Structure

### Standard Layout

```
myproject/
├── cmd/                    # Main applications
│   ├── api/
│   │   └── main.go        # API server entry point
│   └── worker/
│       └── main.go        # Background worker entry point
├── internal/              # Private application code
│   ├── app/              # Application logic
│   ├── domain/           # Domain models
│   └── platform/         # Platform-specific code
├── pkg/                   # Public libraries (reusable)
│   ├── auth/
│   └── logger/
├── api/                   # API definitions (OpenAPI, protobuf)
├── web/                   # Web assets (templates, static files)
├── scripts/               # Build, install, analysis scripts
├── configs/               # Configuration files
├── deployments/           # Deployment configs (docker, k8s)
├── test/                  # Additional test data
├── docs/                  # Documentation
├── examples/              # Example code
├── tools/                 # Supporting tools
├── vendor/                # Vendored dependencies (optional)
├── go.mod                 # Module definition
├── go.sum                 # Dependency checksums
├── Makefile              # Build automation
└── README.md
```

**Key directories:**

| Directory | Purpose | Public/Private |
|-----------|---------|----------------|
| `cmd/` | Main applications (one per binary) | Private |
| `internal/` | Private application code (cannot be imported) | Private |
| `pkg/` | Public libraries (can be imported by others) | Public |
| `api/` | API definitions, schemas | Public |

**Rules:**
- `internal/` cannot be imported by external packages (enforced by Go compiler)
- One `main.go` per `cmd/<app>/` subdirectory
- Keep `pkg/` minimal - most code should be in `internal/`
- Flat is better than nested - avoid deep hierarchies

### Minimal Project

For small projects:

```
myproject/
├── main.go
├── handler.go
├── service.go
├── repository.go
├── go.mod
├── go.sum
└── README.md
```

### Package Naming

```go
// ❌ BAD: Stuttering
auth.AuthService
user.UserRepository
http.HTTPClient

// ✅ GOOD: Concise
auth.Service
user.Repository
http.Client
```

**Rules:**
- Lowercase, single word
- No underscores or mixedCaps
- Avoid generic names (`util`, `common`, `base`, `helper`)
- Name by purpose, not type (`auth`, `logger`, not `structs`, `interfaces`)

## Error Handling

### Basic Pattern

```go
// ✅ GOOD: Immediate error check
result, err := doSomething()
if err != nil {
    return nil, err
}

// ❌ BAD: Deferred error check
result, err := doSomething()
// ... many lines ...
if err != nil {
    return nil, err
}
```

### Error Wrapping

```go
// ✅ GOOD: Wrap errors with context
func processUser(id int) error {
    user, err := fetchUser(id)
    if err != nil {
        return fmt.Errorf("failed to fetch user %d: %w", id, err)
    }
    
    if err := saveUser(user); err != nil {
        return fmt.Errorf("failed to save user %d: %w", id, err)
    }
    
    return nil
}

// Check wrapped errors
err := processUser(123)
if errors.Is(err, sql.ErrNoRows) {
    // Handle specific error
}
```

**Use `%w` for wrapping, `%v` for opaque errors.**

### Custom Errors

```go
// Define sentinel errors for expected conditions
var (
    ErrUserNotFound = errors.New("user not found")
    ErrInvalidInput = errors.New("invalid input")
    ErrUnauthorized = errors.New("unauthorized")
)

// Use in code
func getUser(id int) (*User, error) {
    if id <= 0 {
        return nil, ErrInvalidInput
    }
    
    user := db.FindUser(id)
    if user == nil {
        return nil, ErrUserNotFound
    }
    
    return user, nil
}

// Check in caller
user, err := getUser(id)
if errors.Is(err, ErrUserNotFound) {
    return http.StatusNotFound
}
```

### Error Types

```go
// For errors with additional context
type ValidationError struct {
    Field string
    Value interface{}
    Err   error
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed for field %s: %v", e.Field, e.Err)
}

func (e *ValidationError) Unwrap() error {
    return e.Err
}

// Usage
func validateAge(age int) error {
    if age < 0 {
        return &ValidationError{
            Field: "age",
            Value: age,
            Err:   errors.New("must be non-negative"),
        }
    }
    return nil
}
```

### Error Handling Anti-Patterns

```go
// ❌ BAD: Ignoring errors
result, _ := doSomething()

// ❌ BAD: Generic error messages
if err != nil {
    return errors.New("error")
}

// ❌ BAD: Panic for expected errors
if err != nil {
    panic(err)  // Only use panic for truly unrecoverable situations
}

// ✅ GOOD: Explicit handling
result, err := doSomething()
if err != nil {
    return fmt.Errorf("failed to do something: %w", err)
}
```

## Interfaces

### Accept Interfaces, Return Structs

```go
// ❌ BAD: Returning interface
func NewService() ServiceInterface {
    return &service{}
}

// ✅ GOOD: Returning struct
func NewService() *Service {
    return &Service{}
}

// ✅ GOOD: Accepting interface
func ProcessData(r io.Reader) error {
    // Can accept *os.File, bytes.Buffer, etc.
}
```

### Small Interfaces

```go
// ✅ GOOD: Single-method interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// ✅ GOOD: Compose when needed
type ReadWriter interface {
    Reader
    Writer
}

// ❌ BAD: Large interfaces
type UserService interface {
    CreateUser(ctx context.Context, user *User) error
    GetUser(ctx context.Context, id int) (*User, error)
    UpdateUser(ctx context.Context, user *User) error
    DeleteUser(ctx context.Context, id int) error
    ListUsers(ctx context.Context, filter Filter) ([]*User, error)
    SearchUsers(ctx context.Context, query string) ([]*User, error)
    // ... 10 more methods
}
```

**Rule:** "The bigger the interface, the weaker the abstraction."

### Interface Definition Location

```go
// ✅ GOOD: Define interfaces where they're used (consumer-side)
package handler

type UserRepository interface {
    GetUser(id int) (*User, error)
}

type Handler struct {
    repo UserRepository
}

// Separate implementation
package postgres

type UserRepo struct {
    db *sql.DB
}

func (r *UserRepo) GetUser(id int) (*User, error) {
    // Implementation
}
```

**Rule:** Let consumers define interfaces, not providers.

## Concurrency

### Goroutines

```go
// ✅ GOOD: Launch goroutine
go func() {
    result := compute()
    fmt.Println(result)
}()

// ✅ GOOD: Launch with closure
for _, item := range items {
    item := item  // Capture loop variable
    go func() {
        process(item)
    }()
}

// ❌ BAD: Loop variable capture
for _, item := range items {
    go func() {
        process(item)  // All goroutines will see the same 'item'
    }()
}
```

### Channels

```go
// Unbuffered channel (synchronous)
ch := make(chan int)

// Buffered channel (asynchronous)
ch := make(chan int, 10)

// Send and receive
ch <- 42      // Send
value := <-ch // Receive

// Close channel (sender's responsibility)
close(ch)

// Check if closed
value, ok := <-ch
if !ok {
    // Channel closed
}

// Range over channel (stops when closed)
for value := range ch {
    process(value)
}
```

### Select Statement

```go
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case ch3 <- msg:
    fmt.Println("Sent to ch3")
case <-time.After(1 * time.Second):
    fmt.Println("Timeout")
default:
    fmt.Println("No channel ready")
}
```

### Worker Pool Pattern

```go
func workerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup
    
    // Start workers
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                result := processJob(job)
                results <- result
            }
        }()
    }
    
    // Wait for all workers to finish
    wg.Wait()
    close(results)
}

// Usage
jobs := make(chan Job, 100)
results := make(chan Result, 100)

go workerPool(jobs, results, 5)

// Send jobs
for _, job := range allJobs {
    jobs <- job
}
close(jobs)

// Collect results
for result := range results {
    fmt.Println(result)
}
```

### Context for Cancellation

```go
func doWork(ctx context.Context) error {
    // Create channel for result
    resultCh := make(chan Result)
    errCh := make(chan error)
    
    // Start work in goroutine
    go func() {
        result, err := expensiveOperation()
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- result
    }()
    
    // Wait for result or cancellation
    select {
    case result := <-resultCh:
        return processResult(result)
    case err := <-errCh:
        return fmt.Errorf("operation failed: %w", err)
    case <-ctx.Done():
        return ctx.Err()
    }
}

// Usage
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

err := doWork(ctx)
if errors.Is(err, context.DeadlineExceeded) {
    // Handle timeout
}
```

### Mutex for Shared State

```go
type SafeCounter struct {
    mu    sync.RWMutex
    count map[string]int
}

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count[key]++
}

func (c *SafeCounter) Value(key string) int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.count[key]
}
```

**Rule:** Use `sync.RWMutex` when reads vastly outnumber writes.

### Common Concurrency Patterns

**Fan-out, fan-in:**

```go
func fanOut(input <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        ch := make(chan int)
        channels[i] = ch
        go func() {
            defer close(ch)
            for v := range input {
                ch <- process(v)
            }
        }()
    }
    return channels
}

func fanIn(channels []<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}
```

**Pipeline:**

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Usage
nums := gen(2, 3, 4)
squares := sq(nums)
for s := range squares {
    fmt.Println(s)
}
```

## Testing

### Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"mixed", 1, -1, 0},
        {"zero", 0, 0, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### Subtests

```go
func TestUser(t *testing.T) {
    t.Run("Create", func(t *testing.T) {
        user := NewUser("alice")
        if user.Name != "alice" {
            t.Errorf("expected name alice, got %s", user.Name)
        }
    })
    
    t.Run("Update", func(t *testing.T) {
        user := NewUser("alice")
        user.SetName("bob")
        if user.Name != "bob" {
            t.Errorf("expected name bob, got %s", user.Name)
        }
    })
}
```

### Test Helpers

```go
func TestMain(m *testing.M) {
    // Setup
    setup()
    
    // Run tests
    code := m.Run()
    
    // Teardown
    teardown()
    
    os.Exit(code)
}

func setup() {
    // Initialize test database, etc.
}

func teardown() {
    // Cleanup
}
```

### Mocking with Interfaces

```go
// Define interface
type UserRepository interface {
    GetUser(id int) (*User, error)
}

// Real implementation
type PostgresRepo struct {
    db *sql.DB
}

func (r *PostgresRepo) GetUser(id int) (*User, error) {
    // Real database query
}

// Mock for testing
type MockRepo struct {
    GetUserFunc func(id int) (*User, error)
}

func (m *MockRepo) GetUser(id int) (*User, error) {
    return m.GetUserFunc(id)
}

// Test
func TestService(t *testing.T) {
    mockRepo := &MockRepo{
        GetUserFunc: func(id int) (*User, error) {
            return &User{ID: id, Name: "test"}, nil
        },
    }
    
    service := NewService(mockRepo)
    user, err := service.GetUser(1)
    
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if user.Name != "test" {
        t.Errorf("expected name test, got %s", user.Name)
    }
}
```

### Testing HTTP Handlers

```go
func TestHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()
    
    handler := NewHandler()
    handler.ServeHTTP(w, req)
    
    if w.Code != http.StatusOK {
        t.Errorf("expected status 200, got %d", w.Code)
    }
    
    var user User
    if err := json.NewDecoder(w.Body).Decode(&user); err != nil {
        t.Fatalf("failed to decode response: %v", err)
    }
    
    if user.ID != 1 {
        t.Errorf("expected user ID 1, got %d", user.ID)
    }
}
```

### Benchmarks

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}

func BenchmarkAddParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Add(1, 2)
        }
    })
}
```

Run: `go test -bench=.`

### Coverage

```bash
go test -cover
go test -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Common Patterns

### Constructor Pattern

```go
// ✅ GOOD: New function returns pointer
func NewService(repo Repository) *Service {
    return &Service{
        repo: repo,
    }
}

// ✅ GOOD: Functional options
type ServiceOption func(*Service)

func WithTimeout(d time.Duration) ServiceOption {
    return func(s *Service) {
        s.timeout = d
    }
}

func NewService(opts ...ServiceOption) *Service {
    s := &Service{
        timeout: 30 * time.Second, // default
    }
    
    for _, opt := range opts {
        opt(s)
    }
    
    return s
}

// Usage
svc := NewService(
    WithTimeout(1 * time.Minute),
    WithRetries(3),
)
```

### Builder Pattern (Rare in Go)

```go
// Only use when construction is complex
type RequestBuilder struct {
    method  string
    url     string
    headers map[string]string
    body    io.Reader
}

func NewRequestBuilder() *RequestBuilder {
    return &RequestBuilder{
        headers: make(map[string]string),
    }
}

func (b *RequestBuilder) Method(m string) *RequestBuilder {
    b.method = m
    return b
}

func (b *RequestBuilder) URL(u string) *RequestBuilder {
    b.url = u
    return b
}

func (b *RequestBuilder) Build() (*http.Request, error) {
    return http.NewRequest(b.method, b.url, b.body)
}

// Usage
req, err := NewRequestBuilder().
    Method("POST").
    URL("https://api.example.com").
    Build()
```

### Singleton (Use Sparingly)

```go
var (
    instance *Service
    once     sync.Once
)

func GetInstance() *Service {
    once.Do(func() {
        instance = &Service{}
    })
    return instance
}
```

**Note:** Prefer dependency injection over singletons.

### Adapter Pattern

```go
// Adapt third-party library to your interface
type Logger interface {
    Info(msg string)
    Error(msg string)
}

type ZapAdapter struct {
    logger *zap.Logger
}

func (z *ZapAdapter) Info(msg string) {
    z.logger.Info(msg)
}

func (z *ZapAdapter) Error(msg string) {
    z.logger.Error(msg)
}
```

## Struct Patterns

### Composition Over Inheritance

```go
// ✅ GOOD: Embedding for composition
type User struct {
    ID   int
    Name string
}

type Admin struct {
    User        // Embedded
    Permissions []string
}

// Admin has all User fields
admin := Admin{
    User: User{ID: 1, Name: "alice"},
    Permissions: []string{"read", "write"},
}
fmt.Println(admin.Name) // Directly accessible
```

### Zero Value Usability

```go
// ✅ GOOD: Usable with zero value
type Buffer struct {
    data []byte
}

func (b *Buffer) Write(p []byte) (int, error) {
    b.data = append(b.data, p...)
    return len(p), nil
}

// Usage without initialization
var buf Buffer
buf.Write([]byte("hello")) // Works!
```

### Private Fields, Public Methods

```go
type Account struct {
    balance int // private
}

func (a *Account) Balance() int {
    return a.balance
}

func (a *Account) Deposit(amount int) error {
    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    a.balance += amount
    return nil
}
```

## Performance Optimization

### Preallocate Slices

```go
// ❌ BAD: Append without capacity
var items []Item
for i := 0; i < 1000; i++ {
    items = append(items, Item{})
}

// ✅ GOOD: Preallocate capacity
items := make([]Item, 0, 1000)
for i := 0; i < 1000; i++ {
    items = append(items, Item{})
}
```

### String Builder

```go
// ❌ BAD: String concatenation
var s string
for i := 0; i < 1000; i++ {
    s += "x"
}

// ✅ GOOD: strings.Builder
var sb strings.Builder
sb.Grow(1000) // Preallocate
for i := 0; i < 1000; i++ {
    sb.WriteString("x")
}
s := sb.String()
```

### Avoid Allocations

```go
// ❌ BAD: Allocates on every call
func process(items []int) []int {
    result := make([]int, 0)
    for _, item := range items {
        if item > 0 {
            result = append(result, item)
        }
    }
    return result
}

// ✅ GOOD: Reuse slice
func process(items []int, result []int) []int {
    result = result[:0] // Reset length
    for _, item := range items {
        if item > 0 {
            result = append(result, item)
        }
    }
    return result
}
```

### Sync.Pool for Temporary Objects

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()
    
    buf.Write(data)
    // Use buf
}
```

### Profiling

```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
    
    // Your application code
}
```

Access profiles:
- CPU: `http://localhost:6060/debug/pprof/profile`
- Heap: `http://localhost:6060/debug/pprof/heap`
- Goroutines: `http://localhost:6060/debug/pprof/goroutine`

Analyze:
```bash
go tool pprof http://localhost:6060/debug/pprof/profile
```

## Common Pitfalls

### Range Loop Variable Capture

```go
// ❌ BAD: Captures loop variable
for _, item := range items {
    go func() {
        fmt.Println(item) // All goroutines print last item
    }()
}

// ✅ GOOD: Capture explicitly
for _, item := range items {
    item := item // Reassign
    go func() {
        fmt.Println(item)
    }()
}

// ✅ GOOD: Pass as parameter
for _, item := range items {
    go func(i Item) {
        fmt.Println(i)
    }(item)
}
```

### Nil Interface Gotcha

```go
// ❌ BAD: Interface is not nil
func returnsError() error {
    var p *MyError = nil
    return p // error interface is not nil!
}

err := returnsError()
if err != nil {
    // This block executes!
}

// ✅ GOOD: Return explicit nil
func returnsError() error {
    var p *MyError = nil
    if p == nil {
        return nil
    }
    return p
}
```

### Defer in Loops

```go
// ❌ BAD: Defer accumulates
for _, file := range files {
    f, err := os.Open(file)
    if err != nil {
        return err
    }
    defer f.Close() // Won't run until function returns
}

// ✅ GOOD: Close immediately or use function
for _, file := range files {
    if err := processFile(file); err != nil {
        return err
    }
}

func processFile(filename string) error {
    f, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer f.Close()
    
    // Process file
    return nil
}
```

### Slice Append Gotcha

```go
// ❌ BAD: Original slice affected
a := []int{1, 2, 3}
b := a[:2]
b = append(b, 4)
// a is now [1, 2, 4]

// ✅ GOOD: Copy slice
a := []int{1, 2, 3}
b := make([]int, len(a[:2]))
copy(b, a[:2])
b = append(b, 4)
// a is still [1, 2, 3]
```

### Map Concurrent Access

```go
// ❌ BAD: Concurrent map writes cause panic
m := make(map[string]int)

go func() {
    m["key"] = 1
}()

go func() {
    m["key"] = 2
}()

// ✅ GOOD: Use sync.Map or mutex
var mu sync.Mutex
m := make(map[string]int)

go func() {
    mu.Lock()
    m["key"] = 1
    mu.Unlock()
}()

go func() {
    mu.Lock()
    m["key"] = 2
    mu.Unlock()
}()
```

## Production Best Practices

### Logging

```go
// Use structured logging
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
defer logger.Sync()

logger.Info("user logged in",
    zap.Int("user_id", 123),
    zap.String("ip", "192.168.1.1"),
)

logger.Error("failed to process request",
    zap.Error(err),
    zap.String("request_id", reqID),
)
```

### Configuration

```go
// Use environment variables or config files
import "github.com/spf13/viper"

func loadConfig() (*Config, error) {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")
    viper.AddConfigPath("/etc/myapp/")
    
    viper.SetEnvPrefix("MYAPP")
    viper.AutomaticEnv()
    
    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }
    
    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, err
    }
    
    return &cfg, nil
}
```

### Graceful Shutdown

```go
func main() {
    srv := &http.Server{
        Addr:    ":8080",
        Handler: handler,
    }
    
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()
    
    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    log.Println("Shutting down server...")
    
    // Graceful shutdown with timeout
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }
    
    log.Println("Server exiting")
}
```

### Database Connections

```go
import "database/sql"

func initDB() (*sql.DB, error) {
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        return nil, err
    }
    
    // Connection pool settings
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(5 * time.Minute)
    
    // Verify connection
    if err := db.Ping(); err != nil {
        return nil, err
    }
    
    return db, nil
}
```

### Context Propagation

```go
// Always pass context as first parameter
func fetchUser(ctx context.Context, userID int) (*User, error) {
    // Use context for cancellation, timeouts, and values
    if err := ctx.Err(); err != nil {
        return nil, err
    }
    
    // Pass context to downstream calls
    return db.GetUser(ctx, userID)
}

// HTTP handler
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    
    user, err := fetchUser(ctx, 123)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    json.NewEncoder(w).Encode(user)
}
```

## Tools and Commands

### Essential Commands

```bash
# Format code
go fmt ./...

# Lint code (requires golangci-lint)
golangci-lint run

# Run tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run tests with race detector
go test -race ./...

# Run benchmarks
go test -bench=. ./...

# Build binary
go build -o myapp ./cmd/myapp

# Install dependencies
go mod download

# Tidy dependencies
go mod tidy

# Vendor dependencies
go mod vendor

# Update dependencies
go get -u ./...

# View documentation
go doc fmt.Println

# Run code
go run main.go
```

### Useful Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `golangci-lint` | Comprehensive linter | `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` |
| `gofmt` | Code formatter | Built-in |
| `goimports` | Import formatter | `go install golang.org/x/tools/cmd/goimports@latest` |
| `staticcheck` | Static analysis | `go install honnef.co/go/tools/cmd/staticcheck@latest` |
| `govulncheck` | Vulnerability scanner | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| `dlv` | Debugger | `go install github.com/go-delve/delve/cmd/dlv@latest` |

### Makefile Example

```makefile
.PHONY: build test lint clean

build:
	go build -o bin/myapp ./cmd/myapp

test:
	go test -v -race -cover ./...

lint:
	golangci-lint run

clean:
	rm -rf bin/

install-tools:
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install golang.org/x/tools/cmd/goimports@latest

run:
	go run ./cmd/myapp
```

## Rules

- **ALWAYS check errors immediately** - don't defer error checks unless absolutely necessary.
- **ALWAYS use `context.Context`** as the first parameter of functions that do I/O or long-running work.
- **ALWAYS close resources with defer** immediately after opening them (files, connections, etc.).
- **ALWAYS use `go fmt`** before committing code - no exceptions.
- **ALWAYS run tests with `-race` flag** to catch race conditions.
- **NEVER ignore errors** - at minimum, log them; never use `_` for error returns.
- **NEVER use `panic` for expected errors** - panic only for truly unrecoverable situations (programmer errors).
- **NEVER share memory by communicating** - communicate by sharing memory (use channels over mutexes when possible).
- **NEVER mutate slices/maps without understanding capacity** - be aware of shared underlying arrays.
- **Accept interfaces, return structs** - keep APIs flexible by accepting interfaces but returning concrete types.
- **Define interfaces where they're used**, not where they're implemented (consumer-side).
- **Keep interfaces small** - single-method interfaces are ideal.
- **Use table-driven tests** for comprehensive test coverage with minimal code.
- **Preallocate slices when size is known** - use `make([]T, 0, capacity)`.
- **Use `strings.Builder` for string concatenation** in loops - never concatenate strings with `+`.
- **Pass context to downstream functions** - never create new context in the middle of a call chain.
- **Name packages by purpose, not type** - `auth`, not `structs`; `logger`, not `interfaces`.
- **Avoid stuttering in names** - `user.Repository`, not `user.UserRepository`.

## Quick Reference

### Minimal HTTP Server

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func main() {
    http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
        users := []User{
            {ID: 1, Name: "Alice"},
            {ID: 2, Name: "Bob"},
        }
        
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(users)
    })
    
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### Minimal CLI App

```go
package main

import (
    "flag"
    "fmt"
    "os"
)

func main() {
    name := flag.String("name", "World", "name to greet")
    flag.Parse()
    
    fmt.Printf("Hello, %s!\n", *name)
}
```

### Module Initialization

```bash
# Initialize module
go mod init github.com/myorg/myapp

# Add dependency
go get github.com/pkg/errors

# Remove unused dependencies
go mod tidy
```

## Resources

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Go Proverbs](https://go-proverbs.github.io/)
- [Go Blog](https://go.dev/blog/)
- [Standard Library](https://pkg.go.dev/std)
- [Awesome Go](https://github.com/avelino/awesome-go)
