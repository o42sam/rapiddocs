# Edge Decoration Design Specification

## Overview

The document generation system uses different edge decoration styles based on the document type to create distinct visual identities.

## Formal Documents - Vertical Lines Design

### Visual Layout

For **FORMAL** documents, three vertical lines appear on the right edge of each page:

```
                                              Page Edge →
                                                        |
┌─────────────────────────────────────────────────────┤
│                                                      ║
│  Document Content                                   ║║
│  Text, headings,                                    ║║
│  and paragraphs                                  ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
│                                                   ║ ║║
└───────────────────────────────────────────────────║─║║
                                                    ║ ║║
                                                    ║ ║║
                                             Line 3 ║ ║║
                                             (4pt)  ║ ║║
                                             Color1    ║║
                                                      ║║
                                               Line 2 ║║
                                               (6pt)  ║║
                                               Color2 ║║
                                                       ║
                                                Line 1 ║
                                                (3pt)  ║
                                                Color1 ║
```

### Technical Specifications

#### Line Properties

| Line | Distance from Right Edge | Thickness | Color |
|------|-------------------------|-----------|-------|
| Line 1 | 0.15 inches | 3 points | foreground_color_1 |
| Line 2 | 0.35 inches | 6 points | foreground_color_2 |
| Line 3 | 0.60 inches | 4 points | foreground_color_1 |

#### Color Alternation Pattern

The lines alternate between the two theme colors:
1. **First line** (rightmost, thinnest): Uses `foreground_color_1`
2. **Second line** (middle, thickest): Uses `foreground_color_2`
3. **Third line** (leftmost, medium): Uses `foreground_color_1`

This creates a visual pattern: **Color1 → Color2 → Color1**

#### Positioning Details

- Lines extend from top to bottom of the page (0 to page_height)
- Lines are vertical (straight, not curved)
- Measured from the right edge of the page:
  - Line 1: `page_width - 0.15 inch`
  - Line 2: `page_width - 0.35 inch`
  - Line 3: `page_width - 0.60 inch`

### Design Rationale

1. **Professional Appearance**: Clean vertical lines create a formal, structured look
2. **Color Integration**: Uses the user's selected theme colors for brand consistency
3. **Subtle Visual Interest**: Varying thickness prevents monotony while maintaining formality
4. **Non-Intrusive**: Positioned on the right edge to not interfere with text content
5. **Distinctive**: Clearly distinguishes formal documents from infographic ones

### Code Implementation

```python
# Formal document decorations
if document_type == "formal":
    # Get both foreground colors
    r1, g1, b1 = self._hex_to_rgb(design_spec.foreground_color_1)
    r2, g2, b2 = self._hex_to_rgb(design_spec.foreground_color_2)

    # Define line properties: (x_position, thickness, color_rgb)
    lines = [
        (self.page_width - 0.15*inch, 3, (r1, g1, b1)),   # Line 1
        (self.page_width - 0.35*inch, 6, (r2, g2, b2)),   # Line 2
        (self.page_width - 0.60*inch, 4, (r1, g1, b1))    # Line 3
    ]

    # Draw each line
    for x_pos, thickness, (r, g, b) in lines:
        canvas_obj.setStrokeColorRGB(r, g, b)
        canvas_obj.setLineWidth(thickness)
        canvas_obj.line(x_pos, 0, x_pos, self.page_height)
```

## Infographic Documents - No Edge Decorations

### Visual Layout

For **INFOGRAPHIC** documents, pages have a clean design with NO edge decorations:

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Document Content                                    │
│  Text, headings,                                     │
│  paragraphs, images,                                 │
│  and visualizations                                  │
│                                                      │
│  [Image or Chart]                                    │
│                                                      │
│  More content...                                     │
│                                                      │
│                                                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Design Rationale

1. **Focus on Content**: No distractions from rich visual elements (images, charts)
2. **Modern Clean Look**: Minimalist design suits infographic style
3. **Visual Hierarchy**: Images and charts provide enough visual interest
4. **Space Optimization**: Maximum space for content and visualizations

### Code Implementation

```python
# Infographic document decorations
elif document_type == "infographic":
    logger.debug("Infographic document - skipping edge decorations")
    # No edge decorations drawn
```

## Examples with Different Color Themes

### Ocean Blue Theme
- `foreground_color_1`: #2563EB (Blue)
- `foreground_color_2`: #06B6D4 (Cyan)

**Formal Document Lines:**
- Line 1 (3pt): Blue
- Line 2 (6pt): Cyan
- Line 3 (4pt): Blue

### Corporate Red Theme
- `foreground_color_1`: #DC2626 (Red)
- `foreground_color_2`: #FB923C (Orange)

**Formal Document Lines:**
- Line 1 (3pt): Red
- Line 2 (6pt): Orange
- Line 3 (4pt): Red

### Forest Green Theme
- `foreground_color_1`: #059669 (Green)
- `foreground_color_2`: #14B8A6 (Teal)

**Formal Document Lines:**
- Line 1 (3pt): Green
- Line 2 (6pt): Teal
- Line 3 (4pt): Green

## Logo Watermark (Both Types)

Both formal and infographic documents include an optional logo watermark:

- **Position**: Center of page
- **Size**: 3" x 3" (maintaining aspect ratio)
- **Opacity**: 8% (very subtle)
- **Pages**: Only on content pages (not cover page)
- **Purpose**: Brand reinforcement without interfering with readability

## Summary Comparison

| Aspect | Formal | Infographic |
|--------|--------|-------------|
| Edge Decorations | 3 vertical lines | None |
| Line Colors | Alternating theme colors | N/A |
| Line Thickness | 3pt, 6pt, 4pt | N/A |
| Line Position | Right edge | N/A |
| Page Design Philosophy | Structured, professional | Clean, modern |
| Visual Interest Source | Edge lines + typography | Images + charts |
| Logo Watermark | ✅ Yes (8% opacity) | ✅ Yes (8% opacity) |

## Testing the Design

To verify the edge decoration implementation:

1. **Generate a formal document** with any color theme
2. **Open the PDF** and examine the right edge of pages
3. **Check for:**
   - Three distinct vertical lines
   - Lines running from top to bottom
   - Varying thickness (thinnest, thickest, medium)
   - Color alternation matching the theme
4. **Generate an infographic document** with the same theme
5. **Verify NO edge decorations** appear on pages

## Accessibility Considerations

- Lines are purely decorative and don't convey information
- Color choice doesn't affect document meaning
- Line positioning doesn't interfere with text readability
- Sufficient contrast maintained with white background
- Design works in grayscale if printed in black and white

## Future Enhancement Ideas

- Allow users to customize line thickness
- Add option for left-side lines (mirror effect)
- Support horizontal lines (top/bottom edges)
- Enable/disable decorations independently of document type
- Add gradient effects to lines
- Support custom line patterns (dashed, dotted)

---

**Version**: 1.0
**Last Updated**: 2025-01-07
**Implementation File**: `app/services/pdf_generator.py` (line 35-99)
