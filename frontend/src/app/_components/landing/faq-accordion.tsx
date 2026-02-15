"use client";

import Link from "next/link";
import { useId, useState } from "react";

type FaqItem = {
  question: string;
  answer: string;
};

const FAQ_ITEMS: readonly FaqItem[] = [
  {
    question: "Is this generic AI feedback?",
    answer:
      "No. PeerLens is built to align feedback with review criteria used by the selected funding call and proposal section.",
  },
  {
    question: "Why do I need to sign in?",
    answer:
      "Sign-in connects a review to your account so you can return to it, export it, and delete it later.",
  },
  {
    question: "How should I use PeerLens?",
    answer:
      "Select the funding call, then a proposal application's section heading, then paste one draft section at a time (for example, methodology, impact, or work plan) so the feedback stays specific and actionable.",
  },
  {
    question: "How is my data handled?",
    answer:
      "PeerLens keeps privacy details in one place. Read the full policy on the Privacy page.",
  },
  {
    question: "Can I delete my data?",
    answer:
      "Yes. You can delete a review from its detail page, which removes that review and associated snippet data.",
  },
];

export function FaqAccordion() {
  const rootId = useId();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section
      aria-label="Frequently asked questions"
      className="rounded-3xl bg-[var(--color-surface)] p-6 md:p-9"
    >
      <h2 className="text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">FAQ</h2>
      <div className="mt-5 divide-y divide-[var(--color-border)] rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)]">
        {FAQ_ITEMS.map((item, index) => {
          const isOpen = openIndex === index;
          const buttonId = `${rootId}-button-${index}`;
          const panelId = `${rootId}-panel-${index}`;
          return (
            <article key={item.question}>
              <h3>
                <button
                  aria-controls={panelId}
                  aria-expanded={isOpen}
                  className="flex w-full items-center justify-between gap-3 px-4 py-4 text-left text-sm font-medium text-[var(--color-foreground)] hover:bg-[var(--color-surface-muted)]"
                  data-pl="faq-toggle"
                  id={buttonId}
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  type="button"
                >
                  {item.question}
                  <span aria-hidden="true" className="text-lg leading-none text-[var(--color-muted-foreground)]">
                    {isOpen ? "−" : "+"}
                  </span>
                </button>
              </h3>
              <div
                aria-labelledby={buttonId}
                className="px-4 pb-4 text-sm leading-6 text-[var(--color-muted-foreground)]"
                hidden={!isOpen}
                id={panelId}
                role="region"
              >
                {item.answer}
                {item.question === "How is my data handled?" ? (
                  <>
                    {" "}
                    <Link className="underline" href="/privacy">
                      See Privacy.
                    </Link>
                  </>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
