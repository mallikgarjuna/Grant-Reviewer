import Link from "next/link";

import { DemoTabs } from "./_components/landing/demo-tabs";
import { FaqAccordion } from "./_components/landing/faq-accordion";

import { LANDING_DEMO_TABS } from "@/lib/landing-demo";

const SUPPORTED_CALLS = LANDING_DEMO_TABS.map((tab) => tab.label).join(" · ");

const BENEFITS = [
  {
    title: "Readiness Score",
    description:
      "See an example score and concrete fixes so you know where your draft is weakest.",
  },
  {
    title: "Review Criteria Check",
    description:
      "Feedback is framed around evaluation criteria used in real grant review settings.",
  },
  {
    title: "Time Saved",
    description:
      "Get structured guidance fast before sharing your draft with supervisors or peers.",
  },
] as const;

const HOW_IT_WORKS = [
  "Sign in to your account.",
  "Select your call and section, then paste your draft text.",
  "Get a review with actionable cards and export options.",
] as const;

export default function Home() {
  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-8 md:px-10 md:py-10">
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

      <main className="mt-8 flex flex-col gap-8 md:gap-10">
        <section className="rounded-3xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 md:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
            Sharpen your proposal before you submit
          </p>
          <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight text-[var(--color-foreground)] md:text-5xl">
            Review-criteria-aligned feedback for your grant writing.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--color-muted-foreground)]">
            PeerLens helps you pre-review one proposal section at a time so you can tighten your
            argument before submission.
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

        <section className="rounded-2xl border border-[var(--color-border)] bg-white p-6 md:p-8">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Reviewer #2 anxiety is real.
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--color-muted-foreground)]">
            Rejection often feels arbitrary when expectations are unclear. PeerLens gives you a
            structured pre-review pass so your draft is easier to evaluate and defend.
          </p>
        </section>

        <DemoTabs />

        <section className="grid gap-4 md:grid-cols-3">
          {BENEFITS.map((benefit) => (
            <article
              className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6"
              key={benefit.title}
            >
              <h2 className="text-lg font-medium text-[var(--color-foreground)]">{benefit.title}</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--color-muted-foreground)]">
                {benefit.description}
              </p>
            </article>
          ))}
        </section>

        <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            How it works
          </h2>
          <ol className="mt-5 grid gap-3 md:grid-cols-3">
            {HOW_IT_WORKS.map((step, index) => (
              <li
                className="rounded-xl border border-[var(--color-border)] bg-white p-4 text-sm leading-6 text-[var(--color-foreground)]"
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

        <section className="rounded-2xl border border-[var(--color-border)] bg-white p-6 md:p-8">
          <p className="text-sm font-medium text-[var(--color-muted-foreground)]">
            Supported calls (text-only): {SUPPORTED_CALLS}
          </p>
        </section>

        <FaqAccordion />

        <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-center">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Ready to review your draft?
          </h2>
          <p className="mt-3 text-sm text-[var(--color-muted-foreground)]">
            Sign in to run feedback on your proposal text.
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

      <footer className="mt-10 border-t border-[var(--color-border)] py-6 text-sm text-[var(--color-muted-foreground)]">
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
