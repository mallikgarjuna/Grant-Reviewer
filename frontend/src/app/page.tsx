// frontend/src/app/page.tsx
import Image from "next/image";
import Link from "next/link";

import { DemoTabs } from "./_components/landing/demo-tabs";
import { FaqAccordion } from "./_components/landing/faq-accordion";

const SUPPORTED_CALL_GROUPS = [
  {
    region: "NL",
    programs: ["NWO", "ZonMw"],
  },
  {
    region: "EU/Horizon-Europe",
    programs: ["ERC", "MSCA"],
  },
] as const;

const BENEFITS = [
  {
    title: "Know Your Readiness",
    description:
      "See not just a score, but exactly where you meet the constraints and where you don't.",
  },
  {
    title: "Zero Generic Feedback",
    description:
      "Every comment is linked to a specific NWO/EU rule. No vague 'write clearer' advice.",
  },
  {
    title: "Self-Correction First",
    description:
      "Resolve structural issues and criterial alignment so you can focus on the science.",
  },
] as const;

const HOW_IT_WORKS = [
  {
    key: "step_1",
    badge: "1",
    title: "Draft",
    description: "Bring your draft proposal text.",
    isHighlighted: false,
  },
  {
    key: "step_2",
    badge: "2",
    title: "Target",
    description: "Select your call and section, then paste your proposal draft text.",
    isHighlighted: false,
  },
  {
    key: "step_3",
    badge: "3",
    title: "Refine",
    description:
      "Receive structured, review-criteria-aligned feedback to revise your draft proposal.",
    isHighlighted: false,
  },
] as const;

export default function Home() {
  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-10 md:px-10 md:py-14">
      <a
        className="sr-only focus:not-sr-only focus:absolute focus:left-6 focus:top-4 focus:z-50 focus:rounded-[var(--radius-md)] focus:bg-[var(--color-primary)] focus:px-4 focus:py-2 focus:text-sm focus:text-white"
        href="#main-content"
      >
        Skip to main content
      </a>
      <header className="flex flex-wrap items-start justify-between gap-2 sm:items-center sm:gap-3">
        <Link className="flex items-center gap-2" href="/">
          <Image
            alt="PeerLens"
            className="h-10 w-[180px] object-cover object-center"
            height={640}
            priority
            src="/logo.png"
            width={640}
          />
        </Link>
        <nav
          aria-label="Primary"
          className="flex w-full items-center justify-end gap-2 sm:w-auto sm:justify-start sm:gap-3"
        >
          <Link
            className="inline-flex h-9 items-center justify-center rounded-[var(--radius-md)] px-2 text-xs font-medium text-[var(--color-foreground)] hover:underline sm:h-10 sm:px-3 sm:text-sm"
            href="/privacy"
          >
            Privacy
          </Link>
          <Link
            className="hidden h-9 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-xs font-medium text-[var(--color-foreground)] hover:bg-[var(--color-surface)] sm:inline-flex sm:h-10 sm:px-4 sm:text-sm"
            href="/sign-in"
          >
            Sign In
          </Link>
        </nav>
      </header>

      <main className="mt-12 flex flex-col gap-16 md:gap-20" id="main-content" tabIndex={-1}>
        <section className="rounded-3xl bg-[var(--color-surface)] px-5 py-8 sm:px-7 sm:py-9 md:px-12 md:py-12">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
            THE GRANT APPLICANT’S PRE-REVIEWER
          </p>
          <h1 className="mt-3 max-w-4xl text-6xl font-semibold tracking-tight text-[var(--color-foreground)] [overflow-wrap:anywhere] md:text-7xl">
            Pre-review your grant-proposal
          </h1>
          <ul className="mt-6 flex flex-col gap-2 text-base leading-7 text-[var(--color-muted-foreground)] md:text-lg">
            <li className="flex gap-2">
              <span className="text-[var(--color-primary)]" aria-hidden="true">✓</span>
              <span>Get a criteria-aligned review before you submit.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-[var(--color-primary)]" aria-hidden="true">✓</span>
              <span>Identify weak evidence and unclear claims before the real reviewers do.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-[var(--color-primary)]" aria-hidden="true">✓</span>
              <span>Fast and criteria-specific.</span>
            </li>
          </ul>
          <div className="mt-7 flex flex-wrap items-center gap-4">
            <Link
              className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105"
              data-pl="cta-primary"
              href="/sign-in"
            >
              Check My Draft Now
            </Link>
          </div>
        </section>

        <section className="rounded-3xl bg-[var(--color-surface)] px-6 py-8 md:px-8 md:text-center">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)] md:text-3xl">
            Aligned with NL & EU Standards.
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--color-muted-foreground)] md:mx-auto md:text-base">
            Direct support for NWO, ZonMw and Horizon Europe (ERC/MSCA) funding calls.
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
              <h2 className="text-lg font-medium text-[var(--color-foreground)]">
                {benefit.title}
              </h2>
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
          <ol className="mt-6 grid gap-4 md:grid-cols-3 md:gap-6">
            {HOW_IT_WORKS.map((step) => (
              <li
                className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-5 md:px-6 md:py-6"
                key={step.key}
              >
                <div className="flex items-center gap-3">
                  <span
                    aria-hidden="true"
                    className="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-lg leading-none text-[var(--color-muted-foreground)]"
                  >
                    {step.badge}
                  </span>
                  <h3 className="font-sans text-[1.35rem] font-semibold text-[var(--color-foreground)]">
                    {step.title}
                  </h3>
                </div>
                <p className="mt-3 text-[0.98rem] leading-7 text-[var(--color-muted-foreground)]">
                  {step.description}
                </p>
              </li>
            ))}
          </ol>
        </section>

        <section className="rounded-2xl bg-[var(--color-surface)] px-6 py-6 md:px-8">
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Supported Funding Calls
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {SUPPORTED_CALL_GROUPS.map((group) => (
              <article
                className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] px-4 py-4"
                key={group.region}
              >
                <p className="font-sans text-base font-semibold text-[var(--color-foreground)]">
                  {group.region}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {group.programs.map((program) => (
                    <span
                      className="inline-flex items-center rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1 text-sm font-medium text-[var(--color-foreground)]"
                      key={`${group.region}-${program}`}
                    >
                      {program}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
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
