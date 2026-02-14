"use client";

import { useId, useMemo, useState } from "react";

import {
  DEFAULT_LANDING_DEMO_TAB_ID,
  LANDING_DEMO_TABS,
  type LandingDemoTab,
} from "@/lib/landing-demo";

const TAB_IDS = LANDING_DEMO_TABS.map((tab) => tab.id);

function nextIndex(currentIndex: number, direction: 1 | -1): number {
  const lastIndex = TAB_IDS.length - 1;
  if (direction === 1) {
    return currentIndex === lastIndex ? 0 : currentIndex + 1;
  }
  return currentIndex === 0 ? lastIndex : currentIndex - 1;
}

export function DemoTabs() {
  const tabsRootId = useId();
  const [activeTabId, setActiveTabId] = useState(DEFAULT_LANDING_DEMO_TAB_ID);

  const activeTab = useMemo<LandingDemoTab>(() => {
    return (
      LANDING_DEMO_TABS.find((tab) => tab.id === activeTabId) ??
      LANDING_DEMO_TABS[0]
    );
  }, [activeTabId]);

  function setActiveTabByIndex(index: number): void {
    const nextTab = LANDING_DEMO_TABS[index];
    if (!nextTab) {
      return;
    }
    setActiveTabId(nextTab.id);
  }

  function onTabKeyDown(event: React.KeyboardEvent<HTMLButtonElement>, index: number): void {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      setActiveTabByIndex(nextIndex(index, 1));
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      setActiveTabByIndex(nextIndex(index, -1));
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      setActiveTabByIndex(0);
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      setActiveTabByIndex(LANDING_DEMO_TABS.length - 1);
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setActiveTabByIndex(index);
    }
  }

  return (
    <section
      aria-label="Static feedback demo"
      className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
        Static demo
      </p>
      <p className="mt-3 text-sm leading-6 text-[var(--color-muted-foreground)]">
        Examples only. Sign in to get feedback on your proposal text.
      </p>
      <p className="text-sm leading-6 text-[var(--color-muted-foreground)]">
        Export your review. Delete your data anytime. See <a className="underline" href="/privacy">Privacy</a>.
      </p>

      <div
        aria-label="Supported calls"
        className="mt-5 flex flex-wrap gap-2"
        role="tablist"
      >
        {LANDING_DEMO_TABS.map((tab, index) => {
          const isActive = tab.id === activeTab.id;
          const tabId = `${tabsRootId}-${tab.id}-tab`;
          const panelId = `${tabsRootId}-${tab.id}-panel`;
          return (
            <button
              aria-controls={panelId}
              aria-selected={isActive}
              className={`inline-flex h-10 items-center rounded-full border px-4 text-sm font-medium transition ${
                isActive
                  ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white"
                  : "border-[var(--color-border)] bg-white text-[var(--color-foreground)] hover:bg-[var(--color-surface-muted)]"
              }`}
              data-pl="demo-tab"
              id={tabId}
              key={tab.id}
              onClick={() => setActiveTabByIndex(index)}
              onKeyDown={(event) => onTabKeyDown(event, index)}
              role="tab"
              tabIndex={isActive ? 0 : -1}
              type="button"
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {LANDING_DEMO_TABS.map((tab) => {
        const isActive = tab.id === activeTab.id;
        const tabId = `${tabsRootId}-${tab.id}-tab`;
        const panelId = `${tabsRootId}-${tab.id}-panel`;

        return (
          <section
            aria-labelledby={tabId}
            className="mt-6 rounded-xl border border-[var(--color-border)] bg-white p-5 md:p-6"
            hidden={!isActive}
            id={panelId}
            key={tab.id}
            role="tabpanel"
            tabIndex={0}
          >
            <h3 className="text-lg font-medium text-[var(--color-foreground)]">{tab.label}</h3>
            <p className="mt-3 text-sm leading-7 text-[var(--color-foreground)]">{tab.snippet}</p>

            <div className="mt-6 grid gap-3">
              {tab.cards.map((card) => (
                <article
                  className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4"
                  key={`${tab.id}-${card.criterion}`}
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-muted-foreground)]">
                    {card.criterion}
                  </p>
                  <p className="mt-2 text-sm text-[var(--color-foreground)]">
                    <span className="font-medium">Finding: </span>
                    {card.finding}
                  </p>
                  <p className="mt-1 text-sm text-[var(--color-foreground)]">
                    <span className="font-medium">Suggested fix: </span>
                    {card.suggestedFix}
                  </p>
                  <p className="mt-1 text-sm text-[var(--color-foreground)]">
                    <span className="font-medium">Micro-rewrite (example): </span>
                    {card.microRewriteExample}
                  </p>
                </article>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-muted-foreground)]">
                Readiness score (example)
              </p>
              <p className="mt-2 text-2xl font-semibold text-[var(--color-foreground)]">
                {tab.readinessScore}/100
              </p>
              <div aria-hidden="true" className="mt-2 h-2 rounded-full bg-[var(--color-surface-muted)]">
                <div
                  className="h-2 rounded-full bg-[var(--color-primary)]"
                  style={{ width: `${tab.readinessScore}%` }}
                />
              </div>
            </div>
          </section>
        );
      })}
    </section>
  );
}
