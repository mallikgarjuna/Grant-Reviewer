import { SignIn } from "@clerk/nextjs";

type SearchParams = {
  redirect_url?: string | string[];
  auth_config_error?: string | string[];
};

function firstValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function safeRedirectTarget(rawValue: string | undefined): string {
  if (rawValue && rawValue.startsWith("/") && !rawValue.startsWith("//")) {
    return rawValue;
  }
  return "/app";
}

export default function SignInPage({
  searchParams,
}: {
  searchParams?: SearchParams;
}) {
  const configError = firstValue(searchParams?.auth_config_error) === "1";
  const redirectTarget = safeRedirectTarget(firstValue(searchParams?.redirect_url));

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl items-center justify-center px-6 py-16">
      {configError ? (
        <section className="w-full max-w-lg rounded-2xl border border-red-200 bg-red-50 p-6">
          <h1 className="text-xl font-semibold text-red-900">Authentication config is missing</h1>
          <p className="mt-2 text-sm text-red-800">
            Set real Clerk keys in <code>frontend/.env.local</code> and restart
            <code className="ml-1">npm run dev</code>.
          </p>
          <p className="mt-3 text-sm text-red-700">
            Required keys: <code>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code> and
            <code className="ml-1">CLERK_SECRET_KEY</code>.
          </p>
        </section>
      ) : (
        <SignIn fallbackRedirectUrl="/app" forceRedirectUrl={redirectTarget} />
      )}
    </main>
  );
}
