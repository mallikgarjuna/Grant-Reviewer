export const metadata = {
  title: "PeerLens Privacy",
  description: "How PeerLens handles proposal data in MVP.",
};

export default function PrivacyPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-6 py-12 md:px-10">
      <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">Privacy</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--color-muted-foreground)]">
        PeerLens is designed to help you review proposal text while keeping data handling clear and minimal.
      </p>

      <section className="mt-8 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
        <ul className="space-y-3 text-sm leading-6 text-[var(--color-foreground)]">
          <li>
            PeerLens does not use proposal snippets to train its models.
          </li>
          <li>
            Proposal snippets are retained until you delete them using self-serve deletion.
          </li>
          <li>
            Minimal operational logs and backups may be retained for up to 30 days.
          </li>
        </ul>
      </section>
    </main>
  );
}
