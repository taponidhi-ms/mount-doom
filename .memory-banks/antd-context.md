# Ant Design Context for Mount Doom

## Overview
Mount Doom uses Ant Design (antd) as its primary UI component library for the Next.js frontend. Ant Design is an enterprise-class UI design language and React UI library with high-quality components.

> **Note**: For a comprehensive list of all Ant Design documentation links (design patterns, components, blogs, and guides), see [`antd-llms-reference.txt`](./antd-llms-reference.txt) - the official llms.txt file from ant.design.

## Official Resources
- **Official Website**: https://ant.design
- **LLM Context File**: https://ant.design/llms.txt (also available in this repo as `antd-llms-reference.txt`)
- **Semantic Descriptions**: https://ant.design/llms-semantic.md
- **Documentation**: https://ant.design/docs/react/introduce
- **Components**: https://ant.design/components/overview
- **API Reference**: https://ant.design/docs/react/api
- **Customization**: https://ant.design/docs/react/customize-theme
- **Migration Guide**: https://ant.design/docs/react/migration-v5
- **Next.js Integration**: https://ant.design/docs/react/use-with-next

## Core Components Used in Mount Doom

### Layout & Structure
- **Typography**: `Title`, `Paragraph`, `Text` - Text elements with built-in styling
  - Usage: Page headings, descriptions, and formatted text
  - Example: `<Title level={2}>Persona Generation</Title>`

### Navigation
- **Tabs**: Tab-based navigation for multi-view pages
  - Usage: Switch between Generate/Validate/Simulate and History views
  - Example: `<Tabs items={[{key: '1', label: 'Generate', children: <Form/>}]}/>`

### Data Display
- **Card**: Container for grouped content
  - Usage: Wrapping forms, results, and configuration sections
  - Features: Bordered, with title, extra actions
  
- **Table**: Data table with pagination and sorting
  - Usage: Displaying history/browse results
  - Features: Built-in pagination, column sorting, loading states
  - Example: `<Table columns={columns} dataSource={data} pagination={{...}}/>`

- **Tag**: Labels and status indicators
  - Usage: Showing status, categories, or metadata
  - Example: `<Tag color="success">Completed</Tag>`

### Data Entry
- **Input**: Text input fields
  - `Input` - Single line text
  - `TextArea` - Multi-line text with auto-resize
  - Features: Placeholder, maxLength, onChange handlers
  
- **Button**: Action triggers
  - Types: `primary`, `default`, `text`, `link`
  - States: `loading`, `disabled`
  - Usage: Form submission, navigation, actions
  - Example: `<Button type="primary" loading={loading} onClick={handleSubmit}>Submit</Button>`

- **Select**: Dropdown selection (not currently used but available)
- **Checkbox**: Binary selection (not currently used but available)
- **Radio**: Single selection from options (not currently used but available)

### Feedback
- **message**: Global notification messages
  - Methods: `message.success()`, `message.error()`, `message.warning()`, `message.info()`
  - Usage: Toast notifications for actions
  - Example: `message.success('Persona generated successfully')`

- **Alert**: Inline alert messages
  - Types: `success`, `info`, `warning`, `error`
  - Usage: Displaying errors and information in context
  - Example: `<Alert type="error" message="Failed to load data" />`

- **Spin**: Loading indicator
  - Usage: Showing loading state for async operations
  - Example: `<Spin indicator={<LoadingOutlined />} />`

### Icons
- **@ant-design/icons**: Icon library
  - Commonly used: `LoadingOutlined`, `ArrowLeftOutlined`
  - Usage: Button icons, status indicators, decorative elements
  - Example: `<LoadingOutlined />`

### Layout Components
- **Space**: Spacing wrapper for inline elements
  - Usage: Adding consistent spacing between elements
  - Directions: `horizontal` (default), `vertical`
  - Example: `<Space direction="vertical" size="large">{children}</Space>`

## Ant Design Patterns Used in Mount Doom

### 1. Tab-Based Page Structure
All use case pages follow this pattern:
```typescript
<Tabs
  items={[
    {
      key: 'generate',
      label: 'Generate',
      children: <GenerateForm />
    },
    {
      key: 'history',
      label: 'History',
      children: <HistoryTable />
    }
  ]}
/>
```

### 2. Form Pattern with Loading States
```typescript
<Card>
  <TextArea
    value={prompt}
    onChange={(e) => setPrompt(e.target.value)}
    placeholder="Enter your prompt"
  />
  <Button
    type="primary"
    loading={loading}
    onClick={handleSubmit}
  >
    Generate
  </Button>
</Card>
```

### 3. Table with Pagination
```typescript
<Table
  dataSource={historyData?.items}
  columns={columns}
  loading={historyLoading}
  pagination={{
    current: historyData?.page,
    pageSize: historyData?.page_size,
    total: historyData?.total_count,
    onChange: (page, pageSize) => loadHistory(page, pageSize)
  }}
/>
```

### 4. Error Handling Pattern
```typescript
// Toast notifications
if (response.error) {
  message.error('Failed to generate persona')
}

// Inline errors
{error && <Alert type="error" message={error} showIcon />}
```

### 5. Typography Destructuring
```typescript
const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
```

## Styling Approach

### Inline Styles
- Mount Doom uses inline styles for custom layouts
- Example: `style={{ minHeight: '100vh', padding: '32px' }}`
- Works well with Ant Design's component styling

### Responsive Design
- Ant Design components are responsive by default
- Use Ant Design's grid system for complex layouts (not heavily used in current implementation)
- Tables automatically handle mobile views

### Theme Customization
- Currently using default Ant Design theme
- Can be customized via theme configuration if needed
- Color palette: Primary blue, success green, error red, warning orange

## Accessibility

### Built-in Features
- Ant Design components include ARIA labels
- Keyboard navigation supported
- Focus management handled automatically
- Screen reader compatible

### Best Practices in Mount Doom
- Use semantic HTML with Ant Design components
- Provide meaningful button labels
- Use Alert components for important messages
- Ensure proper heading hierarchy with Typography.Title levels

## Common Patterns & Conventions

### 1. Client-Side Components
All pages using Ant Design must use 'use client' directive:
```typescript
'use client'

import { Button } from 'antd'
```

### 2. Import Pattern
Import specific components, not the entire library:
```typescript
import { Button, Card, Input, Typography } from 'antd'
```

### 3. Loading States
Always show loading feedback:
- Button loading prop for actions
- Spin component for page/section loading
- Table loading prop for data fetching

### 4. User Feedback
Provide feedback for all user actions:
- Success: `message.success()`
- Error: `message.error()` + optional Alert component
- Warning: `message.warning()` for validation issues

### 5. Pagination
Use Table's built-in pagination:
- Control via `pagination` prop
- Handle onChange for page changes
- Display total count and page info

## Performance Considerations

### Component Loading
- Tree shaking works automatically with named imports
- Only imported components are bundled
- No need for manual optimization

### Table Performance
- Use `rowKey` prop for unique keys
- Implement virtual scrolling for large datasets (not currently needed)
- Use pagination to limit rendered rows

## Integration with Next.js

### Client Components
- All Ant Design components require client-side rendering
- Use 'use client' at top of component files
- Works seamlessly with Next.js App Router

### Server Components
- Cannot use Ant Design in server components
- Keep Ant Design usage in client components only
- PageLayout wraps client components properly

## Version Information
- Current Ant Design version: Check package.json
- Using React 18+ compatible version
- Follows latest Ant Design v5 patterns

## Future Enhancements

### Potential Additions
- **Form** component: For complex form validation
- **Modal** component: For dialogs and confirmations
- **Drawer** component: For side panels
- **Tooltip** component: For helpful hints
- **Popconfirm** component: For action confirmations
- **Badge** component: For notifications counts
- **Steps** component: For multi-step workflows

### Theme Customization
- Consider custom color scheme matching brand
- Configure token-based theming
- Add dark mode support

## Troubleshooting

### Common Issues
1. **"Cannot use import statement outside a module"**
   - Solution: Add 'use client' directive

2. **Components not styled**
   - Solution: Ensure antd CSS is imported in root layout

3. **Hydration errors**
   - Solution: Check for client-only code in server components

4. **Icons not displaying**
   - Solution: Import icons from '@ant-design/icons' package

## Learning Resources

### Official Documentation
- Start with: https://ant.design/docs/react/introduce
- Component explorer: https://ant.design/components/overview
- Design principles: https://ant.design/docs/spec/proximity

### Code Examples
- Official demos in documentation
- Mount Doom codebase examples in `frontend/app/` pages
- GitHub examples: https://github.com/ant-design/ant-design/tree/master/components

## Summary

Ant Design provides Mount Doom with:
- ✅ Consistent, professional UI
- ✅ Rich component library
- ✅ Built-in accessibility
- ✅ Responsive design
- ✅ TypeScript support
- ✅ Excellent documentation
- ✅ Active maintenance

**Key Takeaway**: Always check Ant Design documentation when adding new UI features. The library likely has a component or pattern that fits your needs.
