export const APP_CREATE_REVIEW_ROUTE = "/app";
export const APP_REVIEWS_ROUTE = "/app/reviews";
export const PUBLIC_ENTRY_ROUTE = "/";
export const SIGN_IN_ROUTE = "/sign-in";

export function buildReviewDetailRoute(reviewId: string): string {
  return `${APP_REVIEWS_ROUTE}/${reviewId}`;
}
