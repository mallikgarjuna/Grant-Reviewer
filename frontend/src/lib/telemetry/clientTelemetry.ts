type TelemetryPayload = Record<string, unknown>;

export function trackClientEvent(eventName: string, payload: TelemetryPayload): void {
  // Adapter seam for future analytics backends; default to console for now.
  console.info(eventName, payload);
}
