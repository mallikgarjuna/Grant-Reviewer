import type { ComplianceViolation } from "@/lib/bff/types";

type ComplianceBypassModalProps = {
  isOpen: boolean;
  warnings: ComplianceViolation[];
  onCancel: () => void;
  onConfirm: () => void;
  isSubmitting: boolean;
};

export function ComplianceBypassModal(props: ComplianceBypassModalProps) {
  const { isOpen, warnings, onCancel, onConfirm, isSubmitting } = props;

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-xl rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-[var(--color-foreground)]">Submit with warnings?</h2>
        <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
          Your draft has compliance warnings. You can still request a review.
        </p>

        <ul className="mt-4 max-h-48 list-disc space-y-2 overflow-auto pl-5 text-sm text-[var(--color-foreground)]">
          {warnings.map((warning) => (
            <li key={`${warning.node_logical_id}:${warning.rule_id}`}>{warning.message}</li>
          ))}
        </ul>

        <div className="mt-6 flex justify-end gap-3">
          <button
            className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-4 text-sm font-medium text-[var(--color-foreground)]"
            onClick={onCancel}
            type="button"
          >
            Cancel
          </button>
          <button
            className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            onClick={onConfirm}
            type="button"
          >
            {isSubmitting ? "Submitting..." : "Submit Anyway"}
          </button>
        </div>
      </div>
    </div>
  );
}
