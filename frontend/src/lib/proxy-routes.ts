export function shouldUseClerkProxy(pathname: string): boolean {
  return pathname.startsWith("/app") || pathname.startsWith("/api/bff");
}
