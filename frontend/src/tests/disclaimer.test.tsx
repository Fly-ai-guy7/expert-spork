import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import "@/i18n";

describe("DisclaimerBanner", () => {
  it("renders the AI simulation disclaimer", () => {
    render(<DisclaimerBanner />);
    expect(screen.getByText(/AI Simulation Only/i)).toBeInTheDocument();
  });
});
