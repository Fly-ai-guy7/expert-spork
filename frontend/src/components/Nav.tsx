import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { LangToggle } from "./LangToggle";
import { cn } from "@/lib/cn";

export function Nav() {
  const { t } = useTranslation();
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      "px-3 py-2 rounded-md text-sm font-medium",
      isActive ? "bg-brand text-white" : "text-slate-700 hover:bg-slate-100"
    );
  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
        <div className="font-semibold text-brand text-lg">{t("app.name")}</div>
        <nav className="flex gap-1 flex-1">
          <NavLink to="/" className={linkClass} end>
            {t("nav.training")}
          </NavLink>
          <NavLink to="/cases" className={linkClass}>
            {t("nav.cases")}
          </NavLink>
          <NavLink to="/cases/new" className={linkClass}>
            {t("nav.new_case")}
          </NavLink>
          <NavLink to="/instructor" className={linkClass}>
            {t("nav.instructor")}
          </NavLink>
          <NavLink to="/statutes" className={linkClass}>
            {t("nav.statutes")}
          </NavLink>
        </nav>
        <LangToggle />
      </div>
    </header>
  );
}
