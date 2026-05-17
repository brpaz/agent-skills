---
name: readme-writer
version: "1.0.0"
description: "Create and improve README files with structured installation, usage, API, and contribution guidance."
tags: [documentation, readme, markdown, open-source, technical-writing]
---

# README Writer - Comprehensive Documentation Generator

Use this skill when creating or improving README documentation for any software project. Generates professional, comprehensive READMEs that follow best practices and community standards.

## When to Use

- Creating a README for a new project or library
- Improving an outdated or incomplete README
- Standardising README structure across a set of repositories
- Adding installation, usage, API reference, or contribution sections that are missing

## Philosophy

**A great README is**:
- **Scannable** - Structured with clear headings and hierarchy
- **Complete** - Answers "what", "why", "how", and "who"
- **Actionable** - Users can get started in <5 minutes
- **Maintained** - Stays accurate as the project evolves
- **Accessible** - Clear for both beginners and experts

**Core principles**:
- Show, don't tell - Code examples over prose
- Progressive disclosure - Essential info first, details later
- Assume zero context - Don't assume prior knowledge
- Make it skimmable - Use formatting, lists, tables
- Keep it fresh - README is living documentation

## README Structure Template

Every README should follow this structure (adapt as needed):

```markdown
# Project Name

> One-line description (the "elevator pitch")

[Badges: build status, version, license, etc.]

## Quick Start

[Minimal example to get running in <2 minutes]

## Features

- **Feature 1** - Brief description
- **Feature 2** - Brief description
- **Feature 3** - Brief description

## Installation

[Step-by-step installation instructions]

## Usage

[Common use cases with code examples]

## API Reference

[API documentation if applicable]

## Configuration

[Configuration options and environment variables]

## Examples

[More detailed examples]

## Contributing

[How to contribute]

## License

[License information]
```

## Section-by-Section Guide

### 1. Title and Description

**Format**:
```markdown
# Project Name

> One-line description that explains what this does and why it matters.

[Optional: Screenshot or demo GIF for visual projects]
```

**Rules**:
- Title matches repository/package name exactly
- One-liner is **<80 characters**, descriptive, benefit-focused
- Screenshot/GIF only if it adds immediate value (UI, CLI, output)

**Examples**:

✅ **Good**:
```markdown
# Fast JSON Parser

> High-performance JSON parser that's 3x faster than JSON.parse() with zero dependencies.
```

❌ **Bad**:
```markdown
# json-parser-new

> This is a JSON parser.
```

### 2. Badges

**Common badges** (only include if accurate):
- Build status (CI/CD)
- Test coverage
- Version/release
- Downloads/installs
- License
- Language/framework version

**Format**:
```markdown
[![Build Status](https://img.shields.io/github/actions/workflow/status/user/repo/ci.yml?branch=main)](link)
[![npm version](https://img.shields.io/npm/v/package-name)](link)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](link)
```

**Rules**:
- Maximum 5-6 badges - more = clutter
- Only include badges with current information
- Link badges to relevant pages
- Align badges horizontally (one line)

### 3. Quick Start

**Purpose**: Get a working example in <2 minutes.

**Format**:
```markdown
## Quick Start

```bash
npm install package-name
```

```javascript
import { parse } from 'package-name'

const result = parse('{"key": "value"}')
console.log(result.key) // "value"
```
```

**Rules**:
- Installation + minimal working example
- No configuration needed
- No external dependencies
- Copy-pasteable code
- Expected output shown

**For CLIs**:
```markdown
## Quick Start

```bash
npm install -g cli-name
cli-name --help
```

**Example**:
```bash
cli-name input.txt --output result.txt
# Processed input.txt → result.txt (0.5s)
```
```

**For applications**:
```markdown
## Quick Start

```bash
git clone https://github.com/user/repo.git
cd repo
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the app.
```

### 4. Features

**Purpose**: Highlight key capabilities and differentiators.

**Format**:
```markdown
## Features

- **Zero dependencies** - No external packages required
- **TypeScript-first** - Full type safety and IntelliSense support
- **Blazing fast** - 3x faster than alternatives (see [benchmarks](#benchmarks))
- **Tree-shakeable** - Only bundle what you use (~2KB minified)
- **Framework agnostic** - Works with React, Vue, Svelte, vanilla JS
```

**Rules**:
- Lead with benefits, not implementation details
- Bold the key term, explain the benefit
- 3-7 features (most important only)
- Quantify claims ("3x faster") with links to proof
- Make it scannable - bullets, not paragraphs

### 5. Installation

**Purpose**: Complete installation instructions for all supported methods.

**Format**:
```markdown
## Installation

### npm
```bash
npm install package-name
```

### yarn
```bash
yarn add package-name
```

### pnpm
```bash
pnpm add package-name
```

### CDN
```html
<script src="https://unpkg.com/package-name@latest"></script>
```

**Requirements**:
- Node.js >= 18
- Optional: TypeScript >= 5.0 for full type support
```

**Rules**:
- Show all common installation methods
- Include system requirements
- Note optional dependencies
- Specify minimum versions
- Add troubleshooting for known issues

**For global tools**:
```markdown
## Installation

### Global (recommended)
```bash
npm install -g tool-name
```

### Local (project-specific)
```bash
npm install --save-dev tool-name
```
```

**For Docker**:
```markdown
## Installation

### Docker
```bash
docker pull user/image:latest
docker run -p 3000:3000 user/image:latest
```

### Docker Compose
```bash
curl -o compose.yaml https://example.com/compose.yaml
docker compose up
```
```

### 6. Usage

**Purpose**: Show common use cases with real code examples.

**Format**:
```markdown
## Usage

### Basic Example

```javascript
import { createParser } from 'package-name'

const parser = createParser({
  strict: true,
  format: 'json'
})

const result = parser.parse(input)
```

### Advanced Usage

```javascript
// Custom configuration
const parser = createParser({
  strict: false,
  allowComments: true,
  onError: (err) => console.error(err)
})

// Streaming support
for await (const chunk of parser.stream(largeInput)) {
  process(chunk)
}
```

### Integration with Express

```javascript
import express from 'express'
import { middleware } from 'package-name'

const app = express()
app.use(middleware())
```
```

**Rules**:
- Start simple, progress to complex
- Show real-world use cases
- Include comments for clarity
- Demonstrate key features
- Show expected output when helpful
- Link to full API docs for details

**For CLI tools**:
```markdown
## Usage

### Basic Commands

```bash
# Process a file
tool-name input.txt

# With options
tool-name input.txt --format json --output result.json

# Batch processing
tool-name src/*.txt --output dist/
```

### Common Workflows

```bash
# Development
tool-name watch src/ --hot-reload

# Production build
tool-name build --minify --sourcemap
```
```

### 7. API Reference

**Purpose**: Complete, structured API documentation.

**Format** (for libraries):
```markdown
## API Reference

### `createParser(options)`

Creates a new parser instance.

**Parameters**:
- `options` (Object) - Configuration options
  - `strict` (boolean) - Enable strict mode. Default: `true`
  - `format` (string) - Output format: `'json'`, `'xml'`, `'yaml'`. Default: `'json'`
  - `onError` (Function) - Error callback. Optional.

**Returns**: `Parser` - Parser instance

**Example**:
```javascript
const parser = createParser({
  strict: true,
  format: 'json'
})
```

**Throws**:
- `TypeError` - If options are invalid
- `ConfigError` - If format is unsupported

---

### `parser.parse(input)`

Parses input string synchronously.

**Parameters**:
- `input` (string) - Input to parse

**Returns**: `ParsedResult` - Parsed output

**Example**:
```javascript
const result = parser.parse('{"key": "value"}')
console.log(result.key) // "value"
```

---

### Types

```typescript
interface Parser {
  parse(input: string): ParsedResult
  parseAsync(input: string): Promise<ParsedResult>
  stream(input: string): AsyncIterator<ParsedResult>
}

interface ParsedResult {
  data: unknown
  metadata: {
    format: string
    size: number
  }
}
```
```

**Format** (for CLI tools):
```markdown
## API Reference

### Commands

#### `tool-name process <input>`

Process a file or directory.

**Arguments**:
- `<input>` - Input file or directory path

**Options**:
- `-o, --output <path>` - Output path
- `-f, --format <format>` - Output format (json|xml|yaml)
- `--minify` - Minify output
- `-v, --verbose` - Verbose logging

**Examples**:
```bash
tool-name process input.txt
tool-name process src/ --output dist/ --format json
```

#### `tool-name watch <path>`

Watch for file changes.

**Options**:
- `--hot-reload` - Enable hot reload
- `--ignore <pattern>` - Ignore pattern (glob)

**Example**:
```bash
tool-name watch src/ --hot-reload --ignore "*.test.js"
```

### Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
```

**Rules**:
- Document every public API
- Include types/signatures
- Show parameters, return values, exceptions
- Provide examples for each function
- Use consistent formatting
- Link to TypeScript definitions if available

### 8. Configuration

**Purpose**: Document all configuration options.

**Format**:
```markdown
## Configuration

### Configuration File

Create a `.toolrc.json` in your project root:

```json
{
  "format": "json",
  "strict": true,
  "output": "dist/",
  "ignore": ["node_modules", "*.test.js"]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TOOL_API_KEY` | API key for authentication | - |
| `TOOL_LOG_LEVEL` | Log level: `debug`, `info`, `warn`, `error` | `info` |
| `TOOL_TIMEOUT` | Request timeout in milliseconds | `5000` |

**Example**:
```bash
export TOOL_API_KEY=your-key
export TOOL_LOG_LEVEL=debug
```

### Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `strict` | boolean | `true` | Enable strict mode |
| `format` | string | `'json'` | Output format |
| `timeout` | number | `5000` | Timeout in ms |
| `retry` | boolean | `false` | Retry on failure |
```

**Rules**:
- Show configuration file format
- List all options in a table
- Include environment variables
- Specify types and defaults
- Show examples for complex configs

### 9. Examples

**Purpose**: Comprehensive, real-world examples.

**Format**:
```markdown
## Examples

### Example 1: REST API Integration

```javascript
import { createClient } from 'package-name'

const client = createClient({
  baseURL: 'https://api.example.com',
  apiKey: process.env.API_KEY
})

// Fetch data
const response = await client.get('/users')
console.log(response.data)

// Post data
await client.post('/users', {
  name: 'John Doe',
  email: 'john@example.com'
})
```

### Example 2: Express Middleware

```javascript
import express from 'express'
import { authMiddleware } from 'package-name'

const app = express()

app.use(authMiddleware({
  secret: process.env.JWT_SECRET,
  expiresIn: '1h'
}))

app.get('/protected', (req, res) => {
  res.json({ user: req.user })
})

app.listen(3000)
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npx tool-name build --minify
```

### More Examples

See [examples/](./examples/) directory for:
- TypeScript integration example
- React integration example
- Docker deployment example
```

**Rules**:
- Show complete, runnable examples
- Focus on real-world scenarios
- Include error handling
- Link to full example repositories
- Add comments for clarity

### 10. Troubleshooting

**Purpose**: Common issues and solutions.

**Format**:
```markdown
## Troubleshooting

### Error: "Module not found"

**Cause**: Package not installed or wrong path.

**Solution**:
```bash
npm install package-name
```

Verify installation:
```bash
npm list package-name
```

---

### Error: "TypeError: Cannot read property 'x' of undefined"

**Cause**: Missing configuration or invalid input.

**Solution**:
Ensure all required options are provided:
```javascript
const parser = createParser({
  strict: true,  // Required
  format: 'json' // Required
})
```

---

### Performance Issues

**Symptom**: Slow parsing on large files.

**Solution**:
Use streaming API for large inputs:
```javascript
for await (const chunk of parser.stream(largeInput)) {
  process(chunk)
}
```

---

### Still having issues?

- Check [GitHub Issues](https://github.com/user/repo/issues)
- Ask on [Discord](https://discord.gg/community)
- Create a [bug report](https://github.com/user/repo/issues/new)
```

**Rules**:
- List most common issues
- Provide clear solutions
- Include error messages verbatim
- Show diagnostic commands
- Link to support channels

### 11. Contributing

**Purpose**: Guide contributors to help with the project.

**Format**:
```markdown
## Contributing

We welcome contributions! Please follow these steps:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/user/repo.git
cd repo

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

### Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `npm test`
6. Run linter: `npm run lint`
7. Commit: `git commit -m "feat: add amazing feature"`
8. Push: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### Code Style

- Use ESLint config: `npm run lint`
- Format with Prettier: `npm run format`
- Write TypeScript with strict mode
- Add JSDoc comments for public APIs

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm run test:coverage
```

Aim for >80% coverage.

### Pull Request Guidelines

- Keep PRs focused (one feature/fix per PR)
- Update documentation
- Add tests
- Ensure CI passes
- Link related issues

### Code of Conduct

Link to your project's code of conduct when one exists.

### Questions?

Join our [Discord](https://discord.gg/community) or open a [Discussion](https://github.com/user/repo/discussions).
```

**Rules**:
- Make setup instructions clear
- Document coding conventions
- Explain commit message format
- Link to Code of Conduct
- Provide support channels

### 12. License

**Purpose**: Legal information.

**Format**:
```markdown
## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 [Your Name/Organization]
```

**Rules**:
- State license type clearly
- Link to LICENSE file
- Include copyright notice

## Special README Types

### Library/Package README

**Focus**: API documentation, installation, usage examples.

**Must include**:
- Installation (npm/yarn/pnpm)
- Quick start example
- Complete API reference
- TypeScript types
- Browser/Node compatibility
- Bundle size
- Performance benchmarks

### CLI Tool README

**Focus**: Commands, options, workflows.

**Must include**:
- Installation (global + local)
- Command reference
- Exit codes
- Configuration files
- Common workflows
- Piping and scripting examples

### Application README

**Focus**: Setup, running, deployment.

**Must include**:
- Prerequisites (Node version, etc.)
- Environment variables
- Database setup
- Development workflow
- Production deployment
- Docker instructions

### Framework/Boilerplate README

**Focus**: Features, structure, getting started.

**Must include**:
- Tech stack overview
- Project structure
- Getting started guide
- Customization options
- Deployment options
- Migration guides

### Internal Tool README

**Focus**: Purpose, team usage, maintenance.

**Must include**:
- Why this exists (problem solved)
- Who maintains it
- How to use it
- How to deploy updates
- Known limitations
- Runbooks/troubleshooting

## README Writing Process

### Step 1: Analyze the Project

**Gather information**:
- Read existing documentation
- Examine `package.json` / `setup.py` / `Cargo.toml`
- Review source code structure
- Check for configuration files
- Identify framework/language
- Note dependencies
- Review issues/PRs for common questions

**Determine README type**: Library? CLI? Application? Framework?

### Step 2: Identify Target Audience

**Ask**:
- Who will use this?
- What's their experience level?
- What do they need to accomplish?
- What context can I assume?

**Tailor content**:
- Beginners: More explanation, simpler examples
- Experts: Concise, focus on advanced features
- Mixed: Progressive disclosure (basics → advanced)

### Step 3: Draft the Structure

**Create outline**:
1. Title + description
2. Quick start (always)
3. Features
4. Installation
5. Usage (basic → advanced)
6. API reference (if applicable)
7. Configuration
8. Examples
9. Troubleshooting
10. Contributing
11. License

**Adapt structure** based on project type.

### Step 4: Write Section by Section

**For each section**:
- Start with the **goal** (what does the reader need?)
- Write **actionable content** (code over prose)
- Use **examples** liberally
- **Test** code examples (ensure they work)
- **Format** for scannability

### Step 5: Add Visual Elements

**When helpful**:
- **Screenshots** for UIs
- **GIFs** for CLI demos
- **Diagrams** for architecture
- **Tables** for comparisons
- **Code blocks** with syntax highlighting

**Tools**:
- Screenshots: OS native tools
- GIFs: [terminalizer](https://github.com/faressoft/terminalizer), [asciinema](https://asciinema.org/)
- Diagrams: [Mermaid](https://mermaid.js.org/), [Excalidraw](https://excalidraw.com/)

### Step 6: Review and Polish

**Checklist**:
- [ ] All code examples work (tested)
- [ ] Links are valid
- [ ] Grammar/spelling checked
- [ ] Formatting consistent
- [ ] No outdated information
- [ ] Mobile-friendly (GitHub renders well)
- [ ] Accessibility (alt text for images)

**Test the README**:
- Follow your own quick start
- Ask a colleague to review
- Check on different devices

## Advanced Techniques

### Progressive Disclosure

**Principle**: Show essential info first, hide details until needed.

**Example**:
```markdown
## Quick Start

```bash
npm install tool-name
tool-name input.txt
```

<details>
<summary>Advanced configuration options</summary>

### Configuration File

Create `.toolrc.json`:
```json
{
  "format": "json",
  "strict": true,
  "plugins": []
}
```

See [full configuration reference](#configuration).
</details>
```

### Comparison Tables

**When to use**: Comparing features, packages, approaches.

**Example**:
```markdown
## Why This Package?

| Feature | This Package | Alternative A | Alternative B |
|---------|--------------|---------------|---------------|
| Bundle size | 2KB | 50KB | 12KB |
| TypeScript | ✅ Full | ⚠️ Partial | ❌ No |
| Zero deps | ✅ Yes | ❌ No | ✅ Yes |
| Performance | 3x faster | Baseline | 2x faster |
```

### Badges

**Best practices**:
- Use [shields.io](https://shields.io/) for consistent badges
- Only include accurate, up-to-date badges
- Link badges to relevant pages
- Common badges:
  - Build status
  - Version
  - Downloads
  - Coverage
  - License
  - Language version

**Example**:
```markdown
[![CI](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)
[![npm](https://img.shields.io/npm/v/package)](https://www.npmjs.com/package/package)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

### Multilingual READMEs

**For international projects**:

```markdown
# Project Name

English README | Japanese README | Chinese README

> Description in English
```

**Guidelines**:
- Keep default README in English
- Link to translations at the top
- Use language-specific filename: `README.{lang}.md`
- Keep translations in sync

### Versioned Documentation

**For breaking changes between versions**:

```markdown
## Documentation

- **v2.x** (current): See this README
- **v1.x**: See [v1 branch](https://github.com/user/repo/tree/v1)

### Migration from v1 to v2

Link to your migration guide when the project has one.
```

## Common Pitfalls

### ❌ Avoid These Mistakes

| Mistake | Why It's Bad | Fix |
|---------|--------------|-----|
| **No quick start** | Users leave immediately | Add 2-minute example at top |
| **Outdated examples** | Code doesn't work, trust lost | Test all examples, update regularly |
| **Wall of text** | Unreadable, users skip | Use headings, lists, code blocks |
| **Assuming context** | "Just configure X" (what's X?) | Explain everything, link to docs |
| **No installation** | Users can't get started | Clear, step-by-step installation |
| **Jargon overload** | Intimidates new users | Define terms, use plain language |
| **No examples** | API docs alone aren't enough | Show real usage scenarios |
| **Dead links** | Frustrating, unprofessional | Check links regularly |
| **Missing license** | Legal uncertainty | Always include license |
| **No troubleshooting** | Users stuck, open issues | Document common issues |

### Recommended Practices

| Practice | Benefit | Implementation |
|----------|---------|----------------|
| **Test examples** | Users trust code that works | Run examples in CI |
| **Keep it current** | README reflects reality | Update with each release |
| **Use formatting** | Scannable, readable | Headers, lists, tables, code blocks |
| **Show, don't tell** | Code > prose | More examples, less explanation |
| **Be specific** | "3x faster" > "fast" | Quantify claims, link to proof |
| **Link externally** | Don't duplicate docs | Link to guides, API docs, tutorials |
| **Version documentation** | Clear expectations | Note which version docs apply to |
| **Mobile-friendly** | Many read on mobile | Test GitHub rendering |
| **Accessibility** | Everyone can use it | Alt text, semantic headings |

## README Maintenance

### When to Update

**Update README when**:
- Adding/removing features
- Changing APIs
- Updating dependencies
- Fixing common issues (add to troubleshooting)
- Releasing new version
- Changing installation process
- Migrating platforms/frameworks

### Automated Checks

**Use CI to enforce**:
```yaml
# .github/workflows/readme-check.yml
name: README Check

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Check for dead links
      - uses: gaurav-nelson/github-action-markdown-link-check@v1
      
      # Test code examples
      - run: npm install
      - run: npm run test:readme-examples
```

### README Changelog

**For major projects**, track README changes:

```markdown
## Documentation History

- **2025-02-14**: Added Docker deployment guide
- **2025-01-20**: Updated API reference for v2.0
- **2024-12-10**: Added troubleshooting section
```

## Tools and Resources

### Markdown Editors

- [VSCode](https://code.visualstudio.com/) with Markdown extensions
- [Typora](https://typora.io/)
- [MarkText](https://github.com/marktext/marktext)

### Linters and Validators

- [markdownlint](https://github.com/DavidAnson/markdownlint) - Style checker
- [remark](https://github.com/remarkjs/remark) - Markdown processor
- [markdown-link-check](https://github.com/tcort/markdown-link-check) - Link validator

### Templates

- [awesome-readme](https://github.com/matiassingers/awesome-readme) - Examples
- [standard-readme](https://github.com/RichardLitt/standard-readme) - Spec
- [readme.so](https://readme.so/) - Online generator

### Analysis Tools

- [readme-score](https://github.com/clayallsopp/readme-score) - Score your README
- [Hemingway Editor](https://hemingwayapp.com/) - Readability checker

## Examples of Great READMEs

### Open Source Projects

**Libraries**:
- [React](https://github.com/facebook/react) - Clear structure, great examples
- [Vue](https://github.com/vuejs/vue) - Excellent ecosystem links
- [lodash](https://github.com/lodash/lodash) - Comprehensive API docs

**CLI Tools**:
- [ripgrep](https://github.com/BurntSushi/ripgrep) - Detailed benchmarks
- [exa](https://github.com/ogham/exa) - Beautiful formatting
- [bat](https://github.com/sharkdp/bat) - Great screenshots

**Frameworks**:
- [Next.js](https://github.com/vercel/next.js) - Clear quick start
- [Nuxt](https://github.com/nuxt/nuxt) - Excellent badge usage
- [Svelte](https://github.com/sveltejs/svelte) - Concise and complete

## Rules

- **ALWAYS include a quick start** - Users need a working example in <2 minutes.
- **ALWAYS test code examples** - Don't publish code that doesn't work.
- **ALWAYS be specific** - "3x faster" is better than "fast", and "2KB" is better than "lightweight".
- **NEVER assume context** - Explain everything, define all terms.
- **NEVER leave dead links** - Check links before publishing.
- **Use progressive disclosure** - Essential info first, details in collapsible sections.
- **Keep it scannable** - Headings, lists, tables, code blocks, not walls of text.
- **Update with releases** - README must reflect current version.
- **Show real examples** - Include realistic code that users will write.
- **Link to external docs** - Don't duplicate full guides, link to them.
- **Include troubleshooting** - Document common issues and solutions.
- **Make it accessible** - Alt text for images, semantic HTML, clear language.

## Quick Reference

### README Checklist

```markdown
- [ ] Title matches project name
- [ ] One-line description (<80 chars)
- [ ] Badges (if applicable)
- [ ] Quick start (2-minute example)
- [ ] Features list
- [ ] Installation instructions
- [ ] Usage examples (basic → advanced)
- [ ] API reference (if library)
- [ ] Configuration options
- [ ] Examples directory linked
- [ ] Troubleshooting section
- [ ] Contributing guide
- [ ] License information
- [ ] All links valid
- [ ] All code examples tested
- [ ] Grammar/spelling checked
```

### Markdown Quick Reference

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*
`inline code`

[Link text](https://url.com)
![Image alt](https://image.url/image.png)

- Unordered list item
- Another item

1. Ordered list item
2. Another item

> Blockquote

\`\`\`javascript
// Code block
const x = 1
\`\`\`

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

<details>
<summary>Collapsible section</summary>
Hidden content here
</details>
```

## Resources

- [GitHub README Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [awesome-readme](https://github.com/matiassingers/awesome-readme)
- [Make a README](https://www.makeareadme.com/)
- [Art of README](https://github.com/hackergrrl/art-of-readme)
- [Standard README](https://github.com/RichardLitt/standard-readme)
- [Shields.io Badge Generator](https://shields.io/)

## Inputs

- Project source directory (to infer tech stack, dependencies, and entry points)
- Project description, target audience, and any existing documentation fragments

## Outputs

- A comprehensive `README.md` with badges, description, installation, usage, API reference, configuration, and contributing sections tailored to the project type
