import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import type { NextFetchEvent, NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { APP_CREATE_REVIEW_ROUTE } from "@/lib/routes";
import { shouldUseClerkProxy } from "@/lib/proxy-routes";

const isAppRoute = createRouteMatcher(["/app(.*)"]);
const isBffApiRoute = createRouteMatcher(["/api/bff(.*)"]);

function buildReturnBackPath(req: NextRequest): string {
  const path = `${req.nextUrl.pathname}${req.nextUrl.search}`;
  if (path.startsWith("//") || !path.startsWith("/app")) {
    return APP_CREATE_REVIEW_ROUTE;
  }
  return path;
}

function hasMissingClerkEnv(): boolean {
  const publishable = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim();
  const secret = process.env.CLERK_SECRET_KEY?.trim();
  if (!publishable || !secret) {
    return true;
  }
  return publishable.includes("REPLACE_ME") || secret.includes("REPLACE_ME");
}

const clerkProxy = clerkMiddleware(async (auth, req) => {
  if (isBffApiRoute(req)) {
    await auth.protect();
    return;
  }

  if (isAppRoute(req)) {
    const { userId } = await auth();
    if (!userId) {
      const signInUrl = new URL("/sign-in", req.url);
      signInUrl.searchParams.set("redirect_url", buildReturnBackPath(req));
      return NextResponse.redirect(signInUrl);
    }
  }
});

export default function proxy(req: NextRequest, event: NextFetchEvent) {
  if (!shouldUseClerkProxy(req.nextUrl.pathname)) {
    return NextResponse.next();
  }

  if (hasMissingClerkEnv()) {
    if (isAppRoute(req)) {
      const signInUrl = new URL("/sign-in", req.url);
      signInUrl.searchParams.set("auth_config_error", "1");
      signInUrl.searchParams.set("redirect_url", buildReturnBackPath(req));
      return NextResponse.redirect(signInUrl);
    }
    if (isBffApiRoute(req)) {
      return NextResponse.json(
        {
          error: {
            code: "INTERNAL_ERROR",
            message: "Authentication is not configured.",
            details: {
              missing:
                "Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY in frontend/.env.local.",
            },
          },
        },
        { status: 500 },
      );
    }
  }

  return clerkProxy(req, event);
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
