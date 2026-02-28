export type DomainOption = {
  value: string;
  label: string;
};

const DOMAIN_OPTIONS_BY_CALL: Record<string, DomainOption[]> = {
  nwo_veni_2025_preproposal: [
    {
      value: "science_enw",
      label: "ENW / Science pilot (500-word research idea limit)",
    },
  ],
};

export function getDomainOptionsForCall(callCode: string): DomainOption[] {
  return DOMAIN_OPTIONS_BY_CALL[callCode] ?? [];
}
