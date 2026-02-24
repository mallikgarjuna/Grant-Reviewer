type BlockingOverlayProps = {
  isVisible: boolean;
  showTimeoutHint: boolean;
};

export function BlockingOverlay(props: BlockingOverlayProps) {
  const { isVisible, showTimeoutHint } = props;

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-md rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 text-center shadow-xl">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" />
        <p className="mt-3 text-sm font-medium text-[var(--color-foreground)]">Submitting review...</p>
        <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
          Please keep this tab open while we process your request.
        </p>
        {showTimeoutHint ? (
          <p className="mt-3 text-sm text-amber-700">
            This request is taking longer than usual. You can check My Reviews after completion.
          </p>
        ) : null}
      </div>
    </div>
  );
}
