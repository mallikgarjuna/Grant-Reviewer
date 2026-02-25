import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { VeniSubmitForm } from "@/components/submit/VeniSubmitForm";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
  }),
}));

describe("VeniSubmitForm orchestration", () => {
  const originalCrypto = globalThis.crypto;

  beforeEach(() => {
    vi.restoreAllMocks();
    push.mockReset();
    window.localStorage.clear();

    // jsdom doesn't implement scrollIntoView
    window.HTMLElement.prototype.scrollIntoView = vi.fn();

    Object.defineProperty(globalThis, "crypto", {
      value: {
        ...originalCrypto,
        randomUUID: () => "fixed-idempotency-key",
      },
      configurable: true,
    });
  });

  it("200 no-errors path triggers both requests with Idempotency-Key", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url.includes("/api/bff/structured-review")) {
        expect(init?.headers).toMatchObject({
          "Content-Type": "application/json",
          "Idempotency-Key": "fixed-idempotency-key",
        });
        return new Response(JSON.stringify({ review_id: "review-123", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);

    render(<VeniSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "profile" },
    });
    fireEvent.change(screen.getByLabelText("Key Outputs"), {
      target: { value: "outputs" },
    });
    fireEvent.change(screen.getByLabelText("Research Idea"), {
      target: { value: "idea" },
    });

    const submit = await screen.findByRole("button", { name: "Submit" });
    fireEvent.click(submit);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/bff/structured-review",
        expect.objectContaining({ method: "POST" }),
      );
    });
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        "/app/reviews/review-123?submitted_nodes=academic_profile%2Ckey_outputs%2Cresearch_idea",
      );
    });
  });

  it("200 with-errors path waits for user confirmation before second request", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(
          JSON.stringify({
            is_compliant: false,
            errors: [
              {
                node_logical_id: "research_idea",
                rule_id: "word_limit_max",
                severity: "ERROR",
                actual: "150",
                expected: "100",
                message: "Maximum word limit is 100.",
                is_blocking: true,
              },
            ],
            warnings: [],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/structured-review")) {
        return new Response(JSON.stringify({ review_id: "review-456", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);

    render(<VeniSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "profile text" },
    });
    const submit = await screen.findByRole("button", { name: "Submit" });
    fireEvent.click(submit);

    await screen.findByText("Submit with warnings?");
    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
    ).toBe(false);

    fireEvent.click(screen.getByRole("button", { name: "Submit Anyway" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
      ).toBe(true);
    });
  });

  it("422 compliance response prevents structured-review request", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(
          JSON.stringify({
            error: {
              code: "DOMAIN_INVALID",
              message: "domain is not recognized for this call.",
              details: { node_logical_ids: ["research_idea"] },
            },
          }),
          { status: 422 },
        );
      }
      if (url.includes("/api/bff/structured-review")) {
        return new Response(JSON.stringify({ review_id: "review-456", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);

    render(<VeniSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "profile text" },
    });

    // initially not invalid
    const researchIdeaField = screen.getByLabelText("Research Idea");
    expect(researchIdeaField).not.toHaveAttribute("aria-invalid", "true");

    const submit = await screen.findByRole("button", { name: "Submit" });
    fireEvent.click(submit);

    await screen.findByText("Submission blocked");

    // Focus should be shifted and aria-invalid should be applied
    await waitFor(() => {
      expect(researchIdeaField).toHaveAttribute("aria-invalid", "true");
      expect(researchIdeaField).toHaveFocus();
    });

    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
    ).toBe(false);
  });

  it("401 during structured-review redirects to sign-in and preserves draft", async () => {
    const storageKey = "draft_nwo_veni_2025_preproposal_v1";
    window.localStorage.setItem(
      storageKey,
      JSON.stringify({
        academic_profile: "saved draft",
        key_outputs: "",
        research_idea: "",
        domain: null,
      }),
    );

    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url.includes("/api/bff/structured-review")) {
        return new Response(
          JSON.stringify({
            error: {
              code: "UNAUTHORIZED",
              message: "User is not authenticated.",
              details: {},
            },
          }),
          { status: 401 },
        );
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);

    render(<VeniSubmitForm />);

    const submit = await screen.findByRole("button", { name: "Submit" });
    fireEvent.click(submit);

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/sign-in");
    });
    expect(window.localStorage.getItem(storageKey)).not.toBeNull();
  });

  it("submitting only academic_profile sends only non-empty nodes to structured-review", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(
          JSON.stringify({
            is_compliant: false,
            errors: [
              {
                node_logical_id: "key_outputs",
                rule_id: "mandatory_presence",
                severity: "ERROR",
                actual: "missing",
                expected: "present",
                message: "Mandatory section is missing text.",
                is_blocking: true,
              },
            ],
            warnings: [],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/structured-review")) {
        const body = JSON.parse(String(init?.body ?? "{}")) as { nodes?: Array<{ node_logical_id: string }> };
        expect(body.nodes).toEqual([{ node_logical_id: "academic_profile", text: "profile text only" }]);
        return new Response(JSON.stringify({ review_id: "review-999", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);
    render(<VeniSubmitForm />);

    const academicProfile = await screen.findByLabelText("Academic Profile");
    fireEvent.change(academicProfile, { target: { value: "profile text only" } });

    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await screen.findByText("Submit with warnings?");
    fireEvent.click(screen.getByRole("button", { name: "Submit Anyway" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/bff/structured-review",
        expect.objectContaining({ method: "POST" }),
      );
    });
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/app/reviews/review-999?submitted_nodes=academic_profile");
    });
  });

  it("submitting only key_outputs sends only key_outputs node", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(
          JSON.stringify({
            is_compliant: false,
            errors: [
              {
                node_logical_id: "academic_profile",
                rule_id: "mandatory_presence",
                severity: "ERROR",
                actual: "missing",
                expected: "present",
                message: "Mandatory section is missing text.",
                is_blocking: true,
              },
            ],
            warnings: [],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/structured-review")) {
        const body = JSON.parse(String(init?.body ?? "{}")) as { nodes?: Array<{ node_logical_id: string }> };
        expect(body.nodes).toEqual([{ node_logical_id: "key_outputs", text: "key outputs only" }]);
        return new Response(JSON.stringify({ review_id: "review-1000", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);
    render(<VeniSubmitForm />);

    const keyOutputs = await screen.findByLabelText("Key Outputs");
    fireEvent.change(keyOutputs, { target: { value: "key outputs only" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await screen.findByText("Submit with warnings?");
    fireEvent.click(screen.getByRole("button", { name: "Submit Anyway" }));

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/app/reviews/review-1000?submitted_nodes=key_outputs");
    });
  });

  it("submitting only research_idea sends only research_idea node", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/check-compliance")) {
        return new Response(
          JSON.stringify({
            is_compliant: false,
            errors: [
              {
                node_logical_id: "academic_profile",
                rule_id: "mandatory_presence",
                severity: "ERROR",
                actual: "missing",
                expected: "present",
                message: "Mandatory section is missing text.",
                is_blocking: true,
              },
            ],
            warnings: [],
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/structured-review")) {
        const body = JSON.parse(String(init?.body ?? "{}")) as { nodes?: Array<{ node_logical_id: string }> };
        expect(body.nodes).toEqual([{ node_logical_id: "research_idea", text: "research idea only" }]);
        return new Response(JSON.stringify({ review_id: "review-1001", status: "COMPLETED" }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);
    render(<VeniSubmitForm />);

    const researchIdea = await screen.findByLabelText("Research Idea");
    fireEvent.change(researchIdea, { target: { value: "research idea only" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await screen.findByText("Submit with warnings?");
    fireEvent.click(screen.getByRole("button", { name: "Submit Anyway" }));

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/app/reviews/review-1001?submitted_nodes=research_idea");
    });
  });

  it("empty submission is blocked before compliance check", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/calls")) {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "veni-call-id",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });

    vi.stubGlobal("fetch", fetchMock);
    render(<VeniSubmitForm />);

    fireEvent.click(await screen.findByRole("button", { name: "Submit" }));
    expect(
      await screen.findByText("You must fill out at least one section before submitting."),
    ).toBeInTheDocument();

    // Academic profile is the default fallback for complete emptiness
    await waitFor(() => {
      expect(screen.getByLabelText("Academic Profile")).toHaveFocus();
    });

    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/check-compliance")),
    ).toBe(false);
  });
});
