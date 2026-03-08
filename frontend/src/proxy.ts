import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import type { NextFetchEvent, NextRequest } from "next/server";
import { NextResponse } from "next/server";
import {
  getAuthMode,
  getTestBypassConfigError,
  resolveBypassUserId,
} from "@/lib/auth/testBypassAuth";
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

export default async function proxy(req: NextRequest, event: NextFetchEvent) {
  if (!shouldUseClerkProxy(req.nextUrl.pathname)) {
    return NextResponse.next();
  }

  if (getAuthMode() === "test_bypass") {
    const configError = getTestBypassConfigError();
    if (configError) {
      if (isBffApiRoute(req)) {
        return NextResponse.json(
          {
            error: {
              code: "INTERNAL_ERROR",
              message: "Test auth bypass configuration is invalid.",
              details: { reason: configError },
            },
          },
          { status: 500 },
        );
      }
      if (isAppRoute(req)) {
        const signInUrl = new URL("/sign-in", req.url);
        signInUrl.searchParams.set("auth_config_error", "1");
        signInUrl.searchParams.set("redirect_url", buildReturnBackPath(req));
        return NextResponse.redirect(signInUrl);
      }
      return NextResponse.next();
    }

    const bypassUserId = await resolveBypassUserId(req);
    if (isBffApiRoute(req) && !bypassUserId) {
      return NextResponse.json(
        {
          error: {
            code: "UNAUTHORIZED",
            message: "Missing or invalid test bypass auth token.",
            details: {},
          },
        },
        { status: 401 },
      );
    }
    if (isAppRoute(req) && !bypassUserId) {
      const signInUrl = new URL("/sign-in", req.url);
      signInUrl.searchParams.set("redirect_url", buildReturnBackPath(req));
      return NextResponse.redirect(signInUrl);
    }
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
