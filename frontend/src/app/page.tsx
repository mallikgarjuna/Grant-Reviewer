export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-12 md:px-10">
      <header className="rounded-3xl border border-[var(--color-border)] bg-[var(--color-surface)] p-10 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
          Grant Reviewer
        </p>
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight text-[var(--color-foreground)] md:text-5xl">
          Rubric-grounded feedback for stronger grant submissions.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--color-muted-foreground)]">
          Paste a section of your proposal, choose the funding call and section, and get structured
          reviewer cards aligned to expectations.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <a
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105"
            href="/app"
          >
            Start Reviewing
          </a>
          <a
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
            href="/blog"
          >
            Read Guides
          </a>
        </div>
      </header>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
          <h2 className="text-base font-semibold text-[var(--color-foreground)]">Focus</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">
            One clear workflow from snippet to actionable review cards.
          </p>
        </article>
        <article className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
          <h2 className="text-base font-semibold text-[var(--color-foreground)]">Traceability</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">
            Every card ties back to explicit rubric expectations.
          </p>
        </article>
        <article className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
          <h2 className="text-base font-semibold text-[var(--color-foreground)]">Speed</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">
            Synchronous MVP flow with safe retries and idempotency support.
          </p>
        </article>
      </section>
    </main>
  );
}
