# Markdown Editing Guidelines

This document defines markdown formatting standards and best practices to ensure consistency, readability, and compatibility across different markdown parsers and platforms.

## Document Structure

### Headers

- **Sequential Levels**: Use heading levels sequentially without skipping (H1 → H2 → H3, not H1 → H3)
- **Blank Lines**: Always include blank lines before and after headings
- **ATX Style**: Use ATX-style headers (`#`) consistently throughout the document
- **Single Space**: Add exactly one space after the hash marks
- **No Extra Spaces**: Avoid multiple spaces around hash marks

```markdown
# Good
## Good Subheading
### Good Sub-subheading

# Bad
###Bad - No space after hash
##  Bad - Multiple spaces
# Bad
#### Bad - Skipped heading level
```

### Line Length

- **Limit**: Keep lines to 80 characters maximum for better readability
- **Word Wrapping**: Break long lines at natural word boundaries
- **URLs**: Long URLs in links are acceptable exceptions

## Lists

### Formatting

- **Consistent Markers**: Use the same list marker throughout (`*`, `+`, or `-`)
- **Indentation**: Indent nested items with exactly 2 spaces
- **Alignment**: Align list items at the same level consistently
- **Spacing**: Include blank lines around list blocks

```markdown
# Good
* First item
* Second item
  * Nested item
  * Another nested item
* Third item

# Bad
* First item
- Second item (inconsistent marker)
    * Too much indentation
* Third item
```

### Ordered Lists

- **Natural Numbering**: Use `1.` for all items (auto-numbering) or sequential numbers
- **Consistent Style**: Maintain the same numbering style throughout the document

## Whitespace

### Line Endings

- **No Trailing Spaces**: Remove all trailing whitespace from lines
- **Single Newline**: End files with exactly one newline character
- **No Multiple Blanks**: Avoid consecutive blank lines (maximum one blank line)

### Indentation

- **Spaces Only**: Use spaces for indentation, never hard tabs
- **Consistent Width**: Use consistent indentation width (typically 2 or 4 spaces)

## Code

### Code Blocks

- **Language Specification**: Always specify the language for fenced code blocks
- **Consistent Fencing**: Use triple backticks (```) consistently
- **No Trailing Spaces**: Remove trailing spaces from code lines

````markdown
# Good
```python
def example():
    return "Hello, World!"
```

# Bad
```
def example():
    return "Hello, World!"
```
````

### Inline Code

- **Single Backticks**: Use single backticks for inline code
- **Proper Escaping**: Escape backticks within code spans when necessary

## Links and References

### Link Formatting

- **Descriptive Text**: Use meaningful link text that describes the destination
- **Valid URLs**: Ensure all URLs are properly formatted and accessible
- **Reference Style**: Consider using reference-style links for repeated URLs

```markdown
# Good
[Markdown Guide](https://www.markdownguide.org/)
Learn more about [markdown syntax][md-syntax].

# Bad
Click [here](https://www.markdownguide.org/) for more info.
[https://www.markdownguide.org/](https://www.markdownguide.org/)

[md-syntax]: https://www.markdownguide.org/basic-syntax/
```

### Images

- **Alt Text**: Always include descriptive alt text for images
- **Proper Syntax**: Use correct image syntax with alt text and URL

```markdown
# Good
![Screenshot of application dashboard](./images/dashboard.png)

# Bad
![](./images/dashboard.png)
```

## Emphasis and Formatting

### Bold and Italic

- **Consistent Markers**: Use consistent markers for emphasis (`*` or `_`)
- **No Spaces**: Avoid spaces between markers and text
- **Word Boundaries**: Place emphasis markers at word boundaries

```markdown
# Good
This is **bold text** and this is *italic text*.

# Bad
This is** bold text** and this is * italic text *.
```

## Tables

### Structure

- **Proper Alignment**: Use proper column alignment with pipes
- **Header Separation**: Include header separator row with dashes
- **Consistent Spacing**: Maintain consistent spacing for readability

```markdown
# Good
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

# Bad
|Column 1|Column 2|
|--|--|
|Data 1|Data 2
```

## Special Elements

### Horizontal Rules

- **Blank Lines**: Surround horizontal rules with blank lines
- **Consistent Style**: Use consistent horizontal rule syntax

### Blockquotes

- **Proper Indentation**: Use `>` with a space for blockquotes
- **Nested Quotes**: Use `>>` for nested blockquotes

```markdown
# Good
> This is a blockquote.
> It can span multiple lines.

# Bad
>This is a blockquote without proper spacing.
```

## Validation

### Tools

Use markdown linting tools to ensure compliance:

```bash
# Example with markdownlint-cli
markdownlint *.md

# Example with markdownlint-cli2
markdownlint-cli2 "**/*.md"
```

### Common Issues

- Trailing whitespace
- Inconsistent heading levels
- Mixed list marker styles
- Missing language tags in code blocks
- Long lines without proper wrapping
- Multiple consecutive blank lines

## Summary

Following these guidelines ensures:

- **Consistency**: Uniform formatting across all documentation
- **Readability**: Better visual structure and comprehension
- **Compatibility**: Works across different markdown parsers
- **Maintainability**: Easier to review and update content
- **Professionalism**: Clean, polished documentation appearance

These standards help create high-quality markdown documents that are both human-readable and machine-parseable.
