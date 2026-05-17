---
name: vicinae-extensions
description: "Build Vicinae launcher extensions using React/TypeScript with @vicinae/api SDK. USE WHEN creating Vicinae extensions, implementing commands, working with List/Grid/Form/Detail UI components, or integrating with Raycast compatibility layer. Covers extension structure, API usage, development workflow, and best practices."
---

# Vicinae Extensions - React/TypeScript Extension Development

Use this skill when building extensions for Vicinae launcher, a high-performance native Linux launcher with Raycast compatibility. This covers the complete extension development workflow using the `@vicinae/api` TypeScript SDK.

## What is Vicinae?

Vicinae (pronounced "vee-CHEE-nay") is a keyboard-driven command launcher for Linux that integrates with:
- Native OS features (window management, clipboard)
- React/TypeScript extension system
- Raycast extension ecosystem (mostly compatible)
- Global extension store

**Architecture:** Extensions run in Node.js and render through a custom React reconciler to native Qt Widgets (no browser, no Electron, no HTML/CSS).

## Extension File Structure

```
my-extension/
├── package.json           # Extension metadata & dependencies
├── tsconfig.json          # TypeScript configuration
├── src/
│   ├── index.tsx         # Main command (default export)
│   ├── other-command.tsx # Additional commands
│   └── lib/
│       └── utils.ts      # Shared utilities
├── assets/               # Icons, images (optional)
│   └── icon.png
└── README.md            # Extension documentation
```

## package.json Structure

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "title": "My Extension",
  "description": "Brief description of what it does",
  "author": "Your Name",
  "license": "MIT",
  
  "main": "src/index.tsx",
  
  "scripts": {
    "dev": "vicinae dev",
    "build": "vicinae build"
  },
  
  "dependencies": {
    "@vicinae/api": "^0.19.0",
    "react": "^18.2.0"
  },
  
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0"
  },
  
  "commands": [
    {
      "name": "search",
      "title": "Search Items",
      "description": "Search and browse items",
      "mode": "view",
      "keywords": ["find", "lookup"]
    },
    {
      "name": "create",
      "title": "Create Item",
      "description": "Create a new item",
      "mode": "view",
      "keywords": ["new", "add"]
    }
  ],
  
  "preferences": [
    {
      "name": "apiKey",
      "type": "password",
      "required": true,
      "title": "API Key",
      "description": "Your service API key"
    },
    {
      "name": "theme",
      "type": "dropdown",
      "required": false,
      "title": "Theme",
      "description": "UI theme preference",
      "default": "auto",
      "data": [
        { "title": "Auto", "value": "auto" },
        { "title": "Light", "value": "light" },
        { "title": "Dark", "value": "dark" }
      ]
    },
    {
      "name": "maxResults",
      "type": "textfield",
      "required": false,
      "title": "Max Results",
      "description": "Maximum number of results to show",
      "default": "10"
    }
  ]
}
```

### Commands Configuration

Each command must specify:
- `name` - File name in src/ (without .tsx)
- `title` - Display name in launcher
- `description` - What the command does
- `mode` - Always `"view"` for React components
- `keywords` - Optional search aliases

### Preferences Types

| Type | Usage | Value Type |
|------|-------|-----------|
| `textfield` | Single-line text input | string |
| `password` | Masked text input | string |
| `dropdown` | Select from options | string |
| `checkbox` | Boolean toggle | boolean (string "true"/"false") |

## Core UI Components

### List - Search & Browse Interface

The most common UI component for searchable item lists:

```typescript
import { ActionPanel, Action, List, Icon } from '@vicinae/api';
import { useState, useEffect } from 'react';

export default function SearchCommand() {
  const [items, setItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    async function fetchItems() {
      setIsLoading(true);
      const results = await searchAPI(searchText);
      setItems(results);
      setIsLoading(false);
    }
    fetchItems();
  }, [searchText]);

  return (
    <List
      isLoading={isLoading}
      searchBarPlaceholder="Search items..."
      onSearchTextChange={setSearchText}
      throttle
    >
      {items.map((item) => (
        <List.Item
          key={item.id}
          title={item.name}
          subtitle={item.category}
          accessories={[
            { text: item.date },
            { icon: Icon.Star, text: String(item.rating) }
          ]}
          actions={
            <ActionPanel>
              <Action.OpenInBrowser url={item.url} />
              <Action.CopyToClipboard 
                title="Copy URL" 
                content={item.url} 
              />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```

#### List Props

```typescript
interface ListProps {
  children: React.ReactNode;
  isLoading?: boolean;                    // Show loading indicator
  searchBarPlaceholder?: string;          // Placeholder text
  onSearchTextChange?: (text: string) => void;  // Search handler
  throttle?: boolean;                     // Debounce search (default: false)
  isShowingDetail?: boolean;              // Show detail pane
  searchBarAccessory?: React.ReactElement; // Dropdown filter
}
```

#### List.Item Props

```typescript
interface ListItemProps {
  id?: string;
  title: string;
  subtitle?: string;
  accessories?: Accessory[];              // Right-side metadata
  icon?: Icon | string;                   // Left icon
  actions?: React.ReactElement<ActionPanel>;
  detail?: React.ReactElement<List.Item.Detail>;
  keywords?: string[];                    // Search keywords
}

type Accessory = 
  | { text: string; icon?: Icon }
  | { icon: Icon; tooltip?: string }
  | { date: Date }
  | { tag: { value: string; color?: Color } };
```

#### List.Item.Detail - Detailed View

```typescript
<List
  isShowingDetail
  searchBarPlaceholder="Search items..."
>
  <List.Item
    title="Item Name"
    detail={
      <List.Item.Detail
        markdown={`
# Title

Description text with **bold** and *italic*.

![Image](https://example.com/image.png)

\`\`\`typescript
const code = "example";
\`\`\`
        `}
        metadata={
          <List.Item.Detail.Metadata>
            <List.Item.Detail.Metadata.Label
              title="Status"
              text="Active"
              icon={Icon.CheckCircle}
            />
            <List.Item.Detail.Metadata.Separator />
            <List.Item.Detail.Metadata.Link
              title="Website"
              target="https://example.com"
              text="example.com"
            />
            <List.Item.Detail.Metadata.TagList title="Tags">
              <List.Item.Detail.Metadata.TagList.Item
                text="tag1"
                color={Color.Blue}
              />
            </List.Item.Detail.Metadata.TagList>
          </List.Item.Detail.Metadata>
        }
      />
    }
  />
</List>
```

#### List.Section - Grouped Items

```typescript
<List>
  <List.Section title="Recent" subtitle="Last 7 days">
    <List.Item title="Item 1" />
    <List.Item title="Item 2" />
  </List.Section>
  
  <List.Section title="Older">
    <List.Item title="Item 3" />
  </List.Section>
</List>
```

#### List.Dropdown - Filter Dropdown

```typescript
<List
  searchBarAccessory={
    <List.Dropdown
      tooltip="Filter by category"
      value={category}
      onChange={setCategory}
    >
      <List.Dropdown.Item title="All" value="all" />
      <List.Dropdown.Item title="Active" value="active" />
      <List.Dropdown.Item title="Archived" value="archived" />
    </List.Dropdown>
  }
>
  {/* List items */}
</List>
```

### Grid - Visual Grid Interface

For visual content (images, icons, cards):

```typescript
import { ActionPanel, Action, Grid } from '@vicinae/api';

export default function GalleryCommand() {
  const [items, setItems] = useState<Item[]>([]);

  return (
    <Grid
      columns={4}
      aspectRatio="1"
      fit={Grid.Fit.Fill}
      searchBarPlaceholder="Search gallery..."
    >
      <Grid.Section title="Recent">
        {items.map((item) => (
          <Grid.Item
            key={item.id}
            content={item.imageUrl}
            title={item.name}
            subtitle={item.date}
            actions={
              <ActionPanel>
                <Action.OpenInBrowser url={item.url} />
              </ActionPanel>
            }
          />
        ))}
      </Grid.Section>
    </Grid>
  );
}
```

#### Grid Props

```typescript
interface GridProps {
  children: React.ReactNode;
  columns?: number;                       // Number of columns (default: 5)
  aspectRatio?: "1" | "3/2" | "2/3" | "4/3" | "16/9";
  fit?: Grid.Fit;                         // How content fits
  inset?: Grid.Inset;                     // Padding
  isLoading?: boolean;
  searchBarPlaceholder?: string;
  onSearchTextChange?: (text: string) => void;
  throttle?: boolean;
}

enum Grid.Fit {
  Contain = "contain",  // Fit within bounds
  Fill = "fill"         // Fill completely
}

enum Grid.Inset {
  Small = "small",
  Medium = "medium",
  Large = "large"
}
```

### Form - Input Forms

For data collection and settings:

```typescript
import { ActionPanel, Action, Form, showToast, Toast } from '@vicinae/api';
import { useState } from 'react';

interface FormValues {
  name: string;
  email: string;
  category: string;
  priority: string[];
  notes: string;
  enabled: boolean;
  date: Date;
}

export default function CreateCommand() {
  const [nameError, setNameError] = useState<string | undefined>();

  async function handleSubmit(values: FormValues) {
    if (!values.name) {
      setNameError("Name is required");
      return;
    }

    try {
      await createItem(values);
      await showToast({
        style: Toast.Style.Success,
        title: "Item created",
        message: values.name
      });
      // Could use popToRoot() or push() here
    } catch (error) {
      await showToast({
        style: Toast.Style.Failure,
        title: "Failed to create item",
        message: String(error)
      });
    }
  }

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm
            title="Create Item"
            onSubmit={handleSubmit}
          />
        </ActionPanel>
      }
    >
      <Form.TextField
        id="name"
        title="Name"
        placeholder="Enter name"
        error={nameError}
        onChange={() => setNameError(undefined)}
      />
      
      <Form.TextField
        id="email"
        title="Email"
        placeholder="user@example.com"
      />
      
      <Form.Dropdown id="category" title="Category" defaultValue="work">
        <Form.Dropdown.Item value="work" title="Work" />
        <Form.Dropdown.Item value="personal" title="Personal" />
      </Form.Dropdown>
      
      <Form.TagPicker id="priority" title="Priority">
        <Form.TagPicker.Item value="high" title="High" />
        <Form.TagPicker.Item value="medium" title="Medium" />
        <Form.TagPicker.Item value="low" title="Low" />
      </Form.TagPicker>
      
      <Form.TextArea
        id="notes"
        title="Notes"
        placeholder="Additional notes..."
      />
      
      <Form.Checkbox
        id="enabled"
        label="Enable notifications"
        defaultValue={true}
      />
      
      <Form.DatePicker
        id="date"
        title="Due Date"
        defaultValue={new Date()}
      />
      
      <Form.Separator />
      
      <Form.Description text="Fill in all required fields" />
    </Form>
  );
}
```

#### Form Field Types

| Component | Purpose | Value Type |
|-----------|---------|-----------|
| `Form.TextField` | Single-line text | string |
| `Form.TextArea` | Multi-line text | string |
| `Form.PasswordField` | Masked input | string |
| `Form.Dropdown` | Single selection | string |
| `Form.TagPicker` | Multiple selection | string[] |
| `Form.Checkbox` | Boolean toggle | boolean |
| `Form.DatePicker` | Date selection | Date |
| `Form.FilePicker` | File selection | string[] (paths) |
| `Form.Separator` | Visual divider | - |
| `Form.Description` | Help text | - |

#### Form Validation

```typescript
// Real-time validation
<Form.TextField
  id="email"
  title="Email"
  error={emailError}
  onChange={(value) => {
    if (!value.includes('@')) {
      setEmailError("Invalid email");
    } else {
      setEmailError(undefined);
    }
  }}
/>

// Submit-time validation
function handleSubmit(values: FormValues) {
  const errors: Record<string, string> = {};
  
  if (!values.name) errors.name = "Required";
  if (!values.email.includes('@')) errors.email = "Invalid email";
  
  if (Object.keys(errors).length > 0) {
    // Show errors (implementation depends on your approach)
    return;
  }
  
  // Proceed with submission
}
```

### Detail - Markdown Detail View

For displaying detailed information:

```typescript
import { ActionPanel, Action, Detail } from '@vicinae/api';

export default function ShowDetailCommand() {
  const markdown = `
# Main Title

## Section

Description with **bold** and *italic* text.

![Image](https://example.com/image.png)

\`\`\`typescript
const code = "example";
\`\`\`

- List item 1
- List item 2

[Link](https://example.com)
  `;

  return (
    <Detail
      markdown={markdown}
      metadata={
        <Detail.Metadata>
          <Detail.Metadata.Label title="Status" text="Active" />
          <Detail.Metadata.Separator />
          <Detail.Metadata.Link
            title="Website"
            target="https://example.com"
            text="example.com"
          />
          <Detail.Metadata.TagList title="Tags">
            <Detail.Metadata.TagList.Item text="tag1" color={Color.Blue} />
            <Detail.Metadata.TagList.Item text="tag2" color={Color.Green} />
          </Detail.Metadata.TagList>
        </Detail.Metadata>
      }
      actions={
        <ActionPanel>
          <Action.OpenInBrowser url="https://example.com" />
          <Action.CopyToClipboard content={markdown} />
        </ActionPanel>
      }
    />
  );
}
```

## Actions

Actions appear in the ActionPanel and execute commands:

```typescript
import { ActionPanel, Action, Icon } from '@vicinae/api';

<ActionPanel>
  {/* Built-in Actions */}
  <Action.OpenInBrowser 
    url="https://example.com"
    title="Open in Browser"
    icon={Icon.Globe}
  />
  
  <Action.CopyToClipboard
    content="text to copy"
    title="Copy Text"
    shortcut={{ modifiers: ["cmd"], key: "c" }}
  />
  
  <Action.Paste
    content="text to paste"
    title="Paste Text"
  />
  
  <Action.Open
    target="/path/to/file"
    title="Open File"
    application="code"  // Optional: specific app
  />
  
  <Action.ShowInFinder
    path="/path/to/file"
    title="Show in Finder"
  />
  
  <Action.OpenWith
    path="/path/to/file"
    title="Open With..."
  />
  
  {/* Custom Actions */}
  <Action
    title="Custom Action"
    icon={Icon.Bolt}
    shortcut={{ modifiers: ["cmd"], key: "k" }}
    onAction={async () => {
      await performAction();
      await showToast({
        style: Toast.Style.Success,
        title: "Done"
      });
    }}
  />
  
  {/* Form Submit */}
  <Action.SubmitForm
    title="Submit"
    onSubmit={(values) => handleSubmit(values)}
  />
  
  {/* Sections */}
  <ActionPanel.Section title="Primary">
    <Action title="Main Action" onAction={() => {}} />
  </ActionPanel.Section>
  
  <ActionPanel.Section title="Secondary">
    <Action title="Other Action" onAction={() => {}} />
  </ActionPanel.Section>
</ActionPanel>
```

### Keyboard Shortcuts

```typescript
import { Keyboard } from '@vicinae/api';

<Action
  title="Delete"
  shortcut={{ modifiers: ["cmd"], key: "delete" }}
  onAction={() => {}}
/>

// Available modifiers: "cmd", "ctrl", "opt", "shift"
// Keys: letters, numbers, "enter", "delete", "escape", "arrowUp", etc.
```

## Navigation

Push and pop between views:

```typescript
import { List, ActionPanel, Action, Detail, useNavigation } from '@vicinae/api';

function MainList() {
  const { push } = useNavigation();

  return (
    <List>
      <List.Item
        title="View Details"
        actions={
          <ActionPanel>
            <Action
              title="Show Details"
              onAction={() => push(<DetailView itemId="123" />)}
            />
          </ActionPanel>
        }
      />
    </List>
  );
}

function DetailView({ itemId }: { itemId: string }) {
  const { pop } = useNavigation();

  return (
    <Detail
      markdown="# Details"
      actions={
        <ActionPanel>
          <Action title="Go Back" onAction={pop} />
        </ActionPanel>
      }
    />
  );
}
```

### Navigation API

```typescript
const { push, pop } = useNavigation();

// Push new view
push(<ComponentName prop="value" />);

// Pop current view
pop();

// Pop to root (close extension)
import { popToRoot } from '@vicinae/api';
await popToRoot();

// Close current window
import { closeMainWindow } from '@vicinae/api';
await closeMainWindow();
```

## Preferences

Access user preferences from package.json:

```typescript
import { getPreferenceValues } from '@vicinae/api';

interface Preferences {
  apiKey: string;
  theme: string;
  maxResults: string;
}

export default function Command() {
  const preferences = getPreferenceValues<Preferences>();
  
  const apiKey = preferences.apiKey;
  const maxResults = parseInt(preferences.maxResults) || 10;

  // Use preferences...
}
```

## Local Storage

Persist data between sessions:

```typescript
import { LocalStorage } from '@vicinae/api';

// Store data
await LocalStorage.setItem('key', 'value');
await LocalStorage.setItem('user', JSON.stringify({ id: 1, name: 'Alice' }));

// Retrieve data
const value = await LocalStorage.getItem('key');
const userJson = await LocalStorage.getItem('user');
const user = userJson ? JSON.parse(userJson) : null;

// Remove data
await LocalStorage.removeItem('key');

// Clear all
await LocalStorage.clear();

// Get all items
const allItems: LocalStorage.Values = await LocalStorage.allItems();
// Returns: { key1: 'value1', key2: 'value2', ... }
```

## Toast Notifications

Show feedback to users:

```typescript
import { showToast, Toast } from '@vicinae/api';

// Success
await showToast({
  style: Toast.Style.Success,
  title: "Operation completed",
  message: "Details about what happened"
});

// Failure
await showToast({
  style: Toast.Style.Failure,
  title: "Operation failed",
  message: "Error details"
});

// Loading (with progress)
const toast = await showToast({
  style: Toast.Style.Animated,
  title: "Processing..."
});

// Update toast
toast.style = Toast.Style.Success;
toast.title = "Completed";
await toast.show();

// Hide toast
await toast.hide();
```

### Toast Styles

```typescript
enum Toast.Style {
  Success = "success",      // Green checkmark
  Failure = "failure",      // Red X
  Animated = "animated"     // Loading spinner
}
```

## Icons

Built-in icon system:

```typescript
import { Icon } from '@vicinae/api';

<List.Item
  title="Item"
  icon={Icon.Star}
  accessories={[
    { icon: Icon.CheckCircle },
    { icon: Icon.Clock }
  ]}
/>

// Common icons:
Icon.Star
Icon.Heart
Icon.Bookmark
Icon.Tag
Icon.Folder
Icon.Document
Icon.Image
Icon.Video
Icon.Music
Icon.Code
Icon.Terminal
Icon.Globe
Icon.Link
Icon.Mail
Icon.Person
Icon.PersonCircle
Icon.Calendar
Icon.Clock
Icon.Bell
Icon.Checkmark
Icon.CheckCircle
Icon.XmarkCircle
Icon.Warning
Icon.Info
Icon.Trash
Icon.Pencil
Icon.Plus
Icon.Minus
Icon.Multiply
Icon.ArrowUp
Icon.ArrowDown
Icon.ArrowLeft
Icon.ArrowRight
Icon.ChevronUp
Icon.ChevronDown
Icon.ChevronLeft
Icon.ChevronRight
Icon.Download
Icon.Upload
Icon.Cloud
Icon.Eye
Icon.EyeSlash
Icon.Lock
Icon.LockUnlocked
Icon.Gear
Icon.Filter
Icon.MagnifyingGlass
Icon.List
Icon.Grid
Icon.Sidebar
Icon.Window
Icon.Play
Icon.Pause
Icon.Stop
Icon.Forward
Icon.Rewind
```

## Colors

Standard color system:

```typescript
import { Color } from '@vicinae/api';

<List.Item
  accessories={[
    { tag: { value: "Active", color: Color.Green } }
  ]}
/>

// Available colors:
Color.Red
Color.Orange
Color.Yellow
Color.Green
Color.Blue
Color.Purple
Color.Magenta
Color.PrimaryText
Color.SecondaryText
```

## Clipboard

Interact with system clipboard:

```typescript
import { Clipboard } from '@vicinae/api';

// Copy text
await Clipboard.copy("text to copy");

// Copy with metadata (for paste handlers)
await Clipboard.copy("https://example.com", {
  transient: true  // Don't add to clipboard history
});

// Read clipboard
const text = await Clipboard.readText();

// Clear clipboard
await Clipboard.clear();
```

## File Search

Search files indexed by Vicinae:

```typescript
import { FileSearch } from '@vicinae/api';

const results = await FileSearch.search('document');

results.forEach(file => {
  console.log(file.path);     // Full path
  console.log(file.name);     // File name
});

// Use in List
export default function SearchFilesCommand() {
  const [results, setResults] = useState<FileSearch.Result[]>([]);

  return (
    <List
      onSearchTextChange={async (query) => {
        const files = await FileSearch.search(query);
        setResults(files);
      }}
    >
      {results.map((file) => (
        <List.Item
          key={file.path}
          title={file.name}
          subtitle={file.path}
          icon={Icon.Document}
          actions={
            <ActionPanel>
              <Action.Open target={file.path} />
              <Action.ShowInFinder path={file.path} />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```

## Environment

Access environment information:

```typescript
import { environment } from '@vicinae/api';

console.log(environment.commandName);      // Current command name
console.log(environment.extensionName);    // Extension identifier
console.log(environment.extensionPath);    // Extension directory path
console.log(environment.assetsPath);       // Assets directory path
console.log(environment.supportPath);      // Support files directory
```

## Error Handling

Proper error handling patterns:

```typescript
import { showToast, Toast } from '@vicinae/api';

export default function Command() {
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true);
        const data = await fetchAPI();
        setItems(data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
        await showToast({
          style: Toast.Style.Failure,
          title: "Failed to load data",
          message: err instanceof Error ? err.message : String(err)
        });
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  if (error) {
    return (
      <List>
        <List.EmptyView
          title="Error"
          description={error.message}
          icon={Icon.XmarkCircle}
        />
      </List>
    );
  }

  return (
    <List isLoading={isLoading}>
      {/* Items */}
    </List>
  );
}
```

## Empty States

Show helpful empty states:

```typescript
<List>
  {items.length === 0 && !isLoading && (
    <List.EmptyView
      icon={Icon.MagnifyingGlass}
      title="No Results Found"
      description="Try a different search term"
    />
  )}
  {items.map(item => (
    <List.Item key={item.id} title={item.name} />
  ))}
</List>
```

## Development Workflow

### 1. Create Extension

From within Vicinae:
- Open launcher (default: Cmd+Space)
- Search "Create Extension"
- Fill in details
- Press Shift+Enter

Or manually:
```bash
mkdir my-extension
cd my-extension
npm init -y
npm install @vicinae/api react
npm install -D @types/react @types/node typescript
```

### 2. Configure package.json

Add extension metadata (see package.json structure above).

### 3. Create Command

```bash
mkdir src
touch src/index.tsx
```

```typescript
// src/index.tsx
import { List } from '@vicinae/api';

export default function Command() {
  return (
    <List>
      <List.Item title="Hello Vicinae" />
    </List>
  );
}
```

### 4. Run in Dev Mode

```bash
npm run dev
# or
npx @vicinae/api dev
```

This:
- Watches for file changes
- Hot-reloads on save
- Shows "(Dev)" suffix in UI
- Logs to console

### 5. Build for Production

```bash
npm run build
# or
npx @vicinae/api build
```

Produces a bundled extension in `dist/`.

### 6. Install Extension

Copy extension directory to:
```
~/.local/share/vicinae/extensions/
```

Or install from extension store within Vicinae.

## TypeScript Configuration

**tsconfig.json:**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020"],
    "module": "commonjs",
    "jsx": "react",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

## Common Patterns

### Debounced Search

```typescript
import { useEffect, useState } from 'react';
import { List } from '@vicinae/api';

export default function SearchCommand() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      const data = await search(query);
      setResults(data);
      setIsLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <List
      isLoading={isLoading}
      onSearchTextChange={setQuery}
      throttle  // Built-in throttling
    >
      {results.map(result => (
        <List.Item key={result.id} title={result.name} />
      ))}
    </List>
  );
}
```

### Pagination

```typescript
import { useEffect, useState } from 'react';
import { List, ActionPanel, Action } from '@vicinae/api';

export default function PaginatedCommand() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    async function loadMore() {
      const newItems = await fetchPage(page);
      setItems(prev => [...prev, ...newItems]);
      setHasMore(newItems.length > 0);
    }
    loadMore();
  }, [page]);

  return (
    <List>
      {items.map(item => (
        <List.Item key={item.id} title={item.name} />
      ))}
      {hasMore && (
        <List.Item
          title="Load More"
          actions={
            <ActionPanel>
              <Action
                title="Load More"
                onAction={() => setPage(p => p + 1)}
              />
            </ActionPanel>
          }
        />
      )}
    </List>
  );
}
```

### Multi-step Forms

```typescript
import { useState } from 'react';
import { List, Form, ActionPanel, Action, useNavigation } from '@vicinae/api';

function SelectType() {
  const { push } = useNavigation();

  return (
    <List>
      <List.Item
        title="Type A"
        actions={
          <ActionPanel>
            <Action
              title="Select"
              onAction={() => push(<CreateForm type="A" />)}
            />
          </ActionPanel>
        }
      />
    </List>
  );
}

function CreateForm({ type }: { type: string }) {
  const { pop } = useNavigation();

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm
            title="Create"
            onSubmit={async (values) => {
              await createItem({ type, ...values });
              pop();
            }}
          />
        </ActionPanel>
      }
    >
      <Form.TextField id="name" title="Name" />
    </Form>
  );
}

export default SelectType;
```

### Refresh Data

```typescript
import { useState, useCallback } from 'react';
import { List, ActionPanel, Action } from '@vicinae/api';

export default function RefreshableCommand() {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    const data = await fetchData();
    setItems(data);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <List isLoading={isLoading}>
      {items.map(item => (
        <List.Item
          key={item.id}
          title={item.name}
          actions={
            <ActionPanel>
              <Action title="Refresh" onAction={refresh} />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```

## Raycast Compatibility

Vicinae supports most Raycast extensions via `@raycast/api` compatibility layer:

```typescript
// Import from @raycast/api works
import { List, ActionPanel, Action } from '@raycast/api';

// Maps to @vicinae/api internally
```

**Compatibility notes:**
- Most List, Grid, Form, Detail components work
- Some advanced features may not be implemented
- Check Vicinae docs for current API coverage
- Prefer `@vicinae/api` for new extensions

## Testing Extensions

Basic testing approach using Vitest:

```typescript
// src/__tests__/utils.test.ts
import { describe, test, expect } from 'vitest';
import { formatDate } from '../lib/utils';

describe('formatDate', () => {
  test('formats date correctly', () => {
    const date = new Date('2024-01-01');
    expect(formatDate(date)).toBe('Jan 1, 2024');
  });
});
```

Install test dependencies:
```bash
npm install -D vitest
```

Add to package.json:
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

Create vitest.config.ts:
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node'
  }
});
```

## Performance Best Practices

### 1. Virtualization
List and Grid automatically virtualize large datasets - render only visible items.

### 2. Debounce Search
Use `throttle` prop on List/Grid or manual debouncing:

```typescript
<List
  throttle
  onSearchTextChange={setQuery}
>
```

### 3. Memoization
Memoize expensive computations:

```typescript
import { useMemo } from 'react';

const filteredItems = useMemo(
  () => items.filter(item => item.active),
  [items]
);
```

### 4. Lazy Loading
Load data on-demand:

```typescript
useEffect(() => {
  if (shouldLoad) {
    loadData();
  }
}, [shouldLoad]);
```

### 5. Avoid Expensive Renders
Keep component renders lightweight - move heavy logic to useEffect.

## Publishing Extensions

### To Personal Repository
1. Build: `npm run build`
2. Copy to: `~/.local/share/vicinae/extensions/`
3. Refresh Vicinae: Restart or reload extensions

### To Global Extension Store
Submit to [vicinaehq/extensions](https://github.com/vicinaehq/extensions):
1. Fork the repository
2. Add your extension to `extensions/`
3. Create pull request
4. Follow contribution guidelines

Extension structure:
```
extensions/
└── your-extension/
    ├── package.json
    ├── README.md
    ├── src/
    └── assets/
```

## Debugging

### Console Logs
In dev mode, console.log appears in terminal:

```typescript
console.log('Debug info:', data);
console.error('Error:', error);
```

### Toast for Quick Feedback

```typescript
await showToast({
  style: Toast.Style.Failure,
  title: "Debug",
  message: JSON.stringify(data, null, 2)
});
```

### Check Environment

```typescript
import { environment } from '@vicinae/api';
console.log('Extension path:', environment.extensionPath);
console.log('Command:', environment.commandName);
```

## Common Issues

### Issue: "Module not found: @vicinae/api"
**Cause:** Package not installed or wrong version.
**Fix:**
```bash
npm install @vicinae/api@latest react@latest
```

### Issue: Extension not appearing in launcher
**Cause:** package.json commands configuration incorrect.
**Fix:** Verify commands array has correct structure:
```json
{
  "commands": [
    {
      "name": "index",
      "title": "My Command",
      "description": "Description",
      "mode": "view"
    }
  ]
}
```

### Issue: Hot reload not working
**Cause:** Dev mode not running or file outside src/.
**Fix:**
- Ensure `npm run dev` is active
- Place all source files in src/
- Check terminal for errors

### Issue: TypeScript errors
**Cause:** Type definitions missing or mismatched.
**Fix:**
```bash
npm install -D @types/react @types/node
```

### Issue: Build fails
**Cause:** Syntax errors or missing dependencies.
**Fix:**
- Check terminal output for specific error
- Verify all imports are installed
- Run `npm install` to ensure dependencies

## Rules

- **ALWAYS use TypeScript** for type safety and better developer experience.
- **ALWAYS export a default function** from command files.
- **NEVER use HTML/CSS** - Vicinae uses native UI, not web rendering.
- **ALWAYS handle loading states** with `isLoading` prop on List/Grid.
- **ALWAYS handle errors** and show user-friendly feedback via Toast or EmptyView.
- **PREFER @vicinae/api over @raycast/api** for new extensions - better feature coverage.
- **USE throttle prop** for search inputs to avoid excessive API calls.
- **MEMOIZE expensive computations** with useMemo/useCallback.
- **TEST with npm run dev** before building for production.
- **FOLLOW Vicinae conventions** for package.json structure and command naming.
- **USE Icons from Icon enum** rather than custom image files when possible.
- **VALIDATE form inputs** before submission - set error states appropriately.
- **CLEAN UP side effects** in useEffect return functions.
- **USE LocalStorage** for persistence, not files or external databases.
- **PROVIDE meaningful empty states** with EmptyView component.
- **USE environment variables** via getPreferenceValues for configuration.

## Resources

- [Vicinae Documentation](https://docs.vicinae.com)
- [Extension Examples](https://github.com/vicinaehq/extensions)
- [Vicinae GitHub](https://github.com/vicinaehq/vicinae)
- [Discord Community](https://discord.gg/rP4ecD42p7)
- [@vicinae/api on npm](https://www.npmjs.com/package/@vicinae/api)

## Example: Complete Extension

**package.json:**
```json
{
  "name": "github-repos",
  "version": "1.0.0",
  "title": "GitHub Repositories",
  "description": "Search and browse GitHub repositories",
  "main": "src/index.tsx",
  "scripts": {
    "dev": "vicinae dev",
    "build": "vicinae build"
  },
  "dependencies": {
    "@vicinae/api": "^0.19.0",
    "react": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0"
  },
  "commands": [
    {
      "name": "search",
      "title": "Search Repositories",
      "description": "Search GitHub repositories",
      "mode": "view"
    }
  ],
  "preferences": [
    {
      "name": "token",
      "type": "password",
      "required": false,
      "title": "GitHub Token",
      "description": "Optional: for higher rate limits"
    }
  ]
}
```

**src/index.tsx:**
```typescript
import { useState, useEffect } from 'react';
import {
  List,
  ActionPanel,
  Action,
  Icon,
  showToast,
  Toast,
  getPreferenceValues
} from '@vicinae/api';

interface Repo {
  id: number;
  name: string;
  full_name: string;
  description: string;
  html_url: string;
  stargazers_count: number;
  language: string;
}

interface Preferences {
  token?: string;
}

export default function SearchRepositories() {
  const [query, setQuery] = useState('');
  const [repos, setRepos] = useState<Repo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const preferences = getPreferenceValues<Preferences>();

  useEffect(() => {
    if (!query) {
      setRepos([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const headers: HeadersInit = {
          'Accept': 'application/vnd.github.v3+json'
        };
        if (preferences.token) {
          headers['Authorization'] = `token ${preferences.token}`;
        }

        const response = await fetch(
          `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=stars&order=desc`,
          { headers }
        );

        if (!response.ok) {
          throw new Error(`GitHub API error: ${response.status}`);
        }

        const data = await response.json();
        setRepos(data.items || []);
      } catch (error) {
        await showToast({
          style: Toast.Style.Failure,
          title: 'Search failed',
          message: error instanceof Error ? error.message : String(error)
        });
        setRepos([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, preferences.token]);

  return (
    <List
      isLoading={isLoading}
      searchBarPlaceholder="Search GitHub repositories..."
      onSearchTextChange={setQuery}
      throttle
    >
      {repos.length === 0 && !isLoading && query && (
        <List.EmptyView
          icon={Icon.MagnifyingGlass}
          title="No repositories found"
          description="Try a different search term"
        />
      )}
      {repos.map((repo) => (
        <List.Item
          key={repo.id}
          title={repo.name}
          subtitle={repo.full_name}
          accessories={[
            { text: repo.language || 'Unknown' },
            { icon: Icon.Star, text: String(repo.stargazers_count) }
          ]}
          actions={
            <ActionPanel>
              <Action.OpenInBrowser
                url={repo.html_url}
                title="Open in Browser"
              />
              <Action.CopyToClipboard
                title="Copy URL"
                content={repo.html_url}
              />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```

This extension demonstrates:
- Search with debouncing
- API integration with optional auth
- Error handling with toasts
- Empty states
- Accessories for metadata
- Actions for navigation
- Preferences for configuration
