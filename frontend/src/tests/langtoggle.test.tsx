import { describe, it, expect } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { LangToggle } from "@/components/LangToggle";
import i18n from "@/i18n";

describe("LangToggle", () => {
  it("flips the html dir attribute when switched to Arabic", async () => {
    await i18n.changeLanguage("en");
    render(<LangToggle />);
    const btn = screen.getByRole("button", { name: /toggle language/i });
    fireEvent.click(btn);
    expect(document.documentElement.dir).toBe("rtl");
    expect(document.documentElement.lang).toBe("ar");
    fireEvent.click(btn);
    expect(document.documentElement.dir).toBe("ltr");
  });
});
