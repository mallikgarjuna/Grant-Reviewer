const POSTS = [
  {
    slug: "writing-better-grant-snippets",
    title: "How to Write Better Grant Snippets for AI Review",
    summary:
      "A short practical guide to preparing proposal text so rubric-grounded feedback is actionable.",
  },
];

export default function BlogIndexPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-6 py-12 md:px-10">
      <header className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
          Blog
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
          Grant Writing Guides
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--color-muted-foreground)]">
          Practical notes on preparing proposal sections and using rubric-aligned feedback loops.
        </p>
      </header>

      <section className="mt-6 grid gap-4">
        {POSTS.map((post) => (
          <article
            className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm"
            key={post.slug}
          >
            <h2 className="text-xl font-semibold text-[var(--color-foreground)]">{post.title}</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">{post.summary}</p>
            <a
              className="mt-4 inline-flex text-sm font-medium text-[var(--color-primary)] hover:underline"
              href={`/blog/${post.slug}`}
            >
              Read article
            </a>
          </article>
        ))}
      </section>
    </main>
  );
}

