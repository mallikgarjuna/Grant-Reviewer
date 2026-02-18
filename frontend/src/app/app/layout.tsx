"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import {
  APP_CREATE_REVIEW_ROUTE,
  APP_REVIEWS_ROUTE,
  PUBLIC_ENTRY_ROUTE,
  SIGN_IN_ROUTE,
} from "@/lib/routes";

function NavLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      className={`inline-flex h-9 items-center rounded-[var(--radius-md)] px-3 text-sm font-medium transition ${
        isActive
          ? "bg-[var(--color-surface-muted)] text-[var(--color-foreground)]"
          : "text-[var(--color-muted-foreground)] hover:text-[var(--color-foreground)]"
      }`}
      href={href}
    >
      {children}
    </Link>
  );
}

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() ?? "";
  const isClerkConfigured =
    publishableKey.length > 0 && !publishableKey.includes("REPLACE_ME");

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-background)]/95 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6 md:px-10">
          <div className="flex items-center gap-5">
            <Link className="flex items-center" href={PUBLIC_ENTRY_ROUTE}>
              <Image
                alt="PeerLens"
                className="h-7 w-auto object-contain"
                height={28}
                priority
                src="/logo.png"
                width={100}
              />
            </Link>
            <nav aria-label="App navigation" className="flex items-center gap-1">
              <NavLink href={APP_CREATE_REVIEW_ROUTE}>New Review</NavLink>
              <NavLink href={APP_REVIEWS_ROUTE}>My Reviews</NavLink>
            </nav>
          </div>
          <div className="flex items-center">
            {isClerkConfigured ? (
              <UserButton
                afterSignOutUrl={PUBLIC_ENTRY_ROUTE}
                appearance={{
                  elements: {
                    avatarBox: "h-8 w-8",
                  },
                }}
              />
            ) : (
              <Link
                className="inline-flex h-9 items-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-3 text-sm font-medium text-[var(--color-foreground)]"
                href={SIGN_IN_ROUTE}
              >
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>
      {children}
    </>
  );
}
