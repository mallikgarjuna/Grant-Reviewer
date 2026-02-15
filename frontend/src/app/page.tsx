import Link from "next/link";

import { DemoTabs } from "./_components/landing/demo-tabs";
import { FaqAccordion } from "./_components/landing/faq-accordion";

import { LANDING_DEMO_TABS } from "@/lib/landing-demo";

const SUPPORTED_CALLS = LANDING_DEMO_TABS.map((tab) => tab.label).join(" · ");

const BENEFITS = [
  {
    title: "Readiness Snapshot",
    description:
      "See where your section is currently strong and where reviewers may ask for sharper evidence.",
  },
  {
    title: "Criteria-Aligned Review",
    description:
      "Feedback is framed around evaluation criteria used in real funding-call assessments.",
  },
  {
    title: "Faster Iteration",
    description:
      "Refine key sections before sending drafts to supervisors, peers, or internal review support.",
  },
] as const;

const HOW_IT_WORKS = [
  "Sign in and open a review session.",
  "Select your call and section, then paste one draft passage.",
  "Receive structured feedback cards you can revise from or export.",
] as const;

export default function Home() {
  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-10 md:px-10 md:py-14">
      <a
        className="sr-only focus:not-sr-only focus:absolute focus:left-6 focus:top-4 focus:z-50 focus:rounded-[var(--radius-md)] focus:bg-[var(--color-primary)] focus:px-4 focus:py-2 focus:text-sm focus:text-white"
        href="#main-content"
      >
        Skip to main content
      </a>
      <header className="flex items-center justify-between gap-4">
        <Link className="text-lg font-semibold text-[var(--color-foreground)]" href="/">
          PeerLens
        </Link>
        <nav aria-label="Primary" className="flex items-center gap-3">
          <Link
            className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] px-3 text-sm font-medium text-[var(--color-foreground)] hover:underline"
            href="/privacy"
          >
            Privacy
          </Link>
          <Link
            className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-4 text-sm font-medium text-[var(--color-foreground)] hover:bg-[var(--color-surface)]"
            href="/sign-in"
          >
            Sign In
          </Link>
        </nav>
      </header>

      <main className="mt-12 flex flex-col gap-14 md:gap-16" id="main-content" tabIndex={-1}>
        <section className="rounded-3xl bg-[var(--color-surface)] px-7 py-9 md:px-12 md:py-12">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
            Sharpen your proposal before you submit
          </p>
          <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight text-[var(--color-foreground)] md:text-5xl">
            PeerLens helps you pressure-test proposal text before submission.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--color-muted-foreground)] md:text-[1.02rem]">
            Get a focused, criteria-aligned review of one section at a time so your argument is
            clearer before formal evaluation.
          </p>
          <div className="mt-7 flex flex-wrap items-center gap-4">
            <Link
              className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105"
              data-pl="cta-primary"
              href="/sign-in"
            >
              Check My Draft Now
            </Link>
            <p className="text-sm text-[var(--color-muted-foreground)]">
              Supported calls: {SUPPORTED_CALLS}
            </p>
          </div>
        </section>

        <section className="mx-auto w-full max-w-4xl">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Reviewer expectations are often implicit.
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--color-muted-foreground)]">
            When expectations are unclear, strong ideas can read as under-evidenced. PeerLens gives
            you a structured pre-review pass so key sections are easier to evaluate and defend.
          </p>
        </section>

        <DemoTabs />

        <section className="rounded-3xl bg-[var(--color-surface)] px-6 py-8 md:px-8 md:py-10">
          <div className="grid gap-6 md:grid-cols-3">
          {BENEFITS.map((benefit) => (
            <article
              className="border-l-2 border-[var(--color-border)] pl-4"
              key={benefit.title}
            >
              <h2 className="text-lg font-medium text-[var(--color-foreground)]">{benefit.title}</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">
                {benefit.description}
              </p>
            </article>
          ))}
          </div>
        </section>

        <section className="rounded-3xl bg-[var(--color-surface)] px-6 py-8 md:px-8 md:py-10">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            How it works
          </h2>
          <ol className="mt-5 grid gap-3 md:grid-cols-3">
            {HOW_IT_WORKS.map((step, index) => (
              <li
                className="rounded-xl bg-white/75 p-4 text-sm leading-6 text-[var(--color-foreground)]"
                key={step}
              >
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-muted-foreground)]">
                  Step {index + 1}
                </p>
                <p className="mt-2">{step}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="rounded-2xl bg-[var(--color-surface)] px-6 py-6 md:px-8">
          <p className="text-sm font-medium text-[var(--color-muted-foreground)]">
            Supported calls (text-only): {SUPPORTED_CALLS}
          </p>
        </section>

        <FaqAccordion />

        <section className="rounded-3xl bg-[var(--color-surface)] px-8 py-10 text-center">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Ready to review a section before submission?
          </h2>
          <p className="mt-3 text-sm text-[var(--color-muted-foreground)]">
            Sign in to run a structured review on your proposal text.
          </p>
          <Link
            className="mt-6 inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105"
            data-pl="cta-primary"
            href="/sign-in"
          >
            Check My Draft Now
          </Link>
        </section>
      </main>

      <footer className="mt-16 border-t border-[var(--color-border)] py-6 text-sm text-[var(--color-muted-foreground)]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p>© 2026 PeerLens</p>
          <Link className="hover:underline" href="/privacy">
            Privacy
          </Link>
        </div>
      </footer>
    </div>
  );
}
