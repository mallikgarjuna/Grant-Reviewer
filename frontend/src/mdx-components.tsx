import type { MDXComponents } from "mdx/types";

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: (props) => (
      <h1
        className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]"
        {...props}
      />
    ),
    h2: (props) => (
      <h2
        className="mt-8 text-2xl font-semibold tracking-tight text-[var(--color-foreground)]"
        {...props}
      />
    ),
    p: (props) => (
      <p className="mt-4 text-base leading-7 text-[var(--color-foreground)]" {...props} />
    ),
    a: (props) => (
      <a
        className="text-[var(--color-primary)] underline-offset-2 hover:underline"
        {...props}
      />
    ),
    ...components,
  };
}
