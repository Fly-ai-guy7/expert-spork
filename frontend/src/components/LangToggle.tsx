import { useTranslation } from "react-i18next";

export function LangToggle() {
  const { i18n } = useTranslation();
  const flip = () => {
    const next = i18n.language === "ar" ? "en" : "ar";
    i18n.changeLanguage(next);
  };
  return (
    <button
      onClick={flip}
      className="rounded-md border px-3 py-1 text-sm hover:bg-slate-100"
      aria-label="Toggle language"
    >
      {i18n.language === "ar" ? "EN" : "ع"}
    </button>
  );
}
