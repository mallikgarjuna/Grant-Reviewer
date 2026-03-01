export type DomainOption = {
  value: string;
  label: string;
};

// Deprecated shim retained for import stability; runtime options are backend-driven.
export function getDomainOptionsForCall(_: string): DomainOption[] {
  return [];
}
