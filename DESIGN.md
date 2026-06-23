# 智训评 Design System

## Visual Theme

Physical scene: a teacher or mentor checking a practical-training queue on a bright office monitor, where dense information needs to stay calm and trustworthy. The strategy is restrained product UI: white working surfaces, a deep operational sidebar, and technology blue reserved for decisive actions and current state.

## Color Tokens

```css
:root {
  --ste-primary: oklch(0.52 0.22 262);
  --ste-primary-hover: oklch(0.47 0.22 262);
  --ste-primary-soft: oklch(0.95 0.03 262);
  --ste-sidebar: oklch(0.22 0.055 257);
  --ste-sidebar-hover: oklch(0.27 0.065 257);
  --ste-bg: oklch(0.975 0.006 255);
  --ste-surface: oklch(1 0 0);
  --ste-surface-subtle: oklch(0.985 0.004 255);
  --ste-ink: oklch(0.24 0.025 257);
  --ste-muted: oklch(0.51 0.025 257);
  --ste-border: oklch(0.90 0.012 255);
  --ste-success: oklch(0.62 0.15 154);
  --ste-warning: oklch(0.74 0.15 72);
  --ste-danger: oklch(0.60 0.20 27);
}
```

`--ste-primary` resolves to the required brand blue `#165DFF` for browser color compatibility in the implementation.

## Typography

- Family: Inter, PingFang SC, Microsoft YaHei, system sans-serif.
- Product scale: 12, 13, 14, 16, 18, 22, 28px.
- Headings use weight 600, body copy stays at 14px / 20px for scanning.

## Components

- Buttons: Element Plus default geometry, primary blue for irreversible or forward actions.
- Surfaces: 8px radius, thin cool-gray border, no soft decorative shadow.
- Data: grouped tables with quiet row dividers; selected state is blue tint plus text/icon signal.
- Navigation: 220px navy sidebar, active item as a solid blue block; collapsed width 64px.

## Layout

- Header: 64px fixed-height operational status bar.
- Content: 24px desktop padding, 16px on smaller laptop widths.
- Dashboard: 12-column grid with dense charts and work queues, collapsing at 1200px and 768px.

## Motion

- 180ms ease-out for navigation, buttons, and overlays.
- Reduced-motion users receive instant state transitions.
