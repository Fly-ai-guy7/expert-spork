import { useTranslation } from "react-i18next";

export function DisclaimerBanner() {
  const { t } = useTranslation();
  return (
    <div className="sticky top-0 z-50 bg-rose-50 border-b border-rose-200 text-rose-900 text-xs sm:text-sm px-4 py-2 text-center">
      ⚠ {t("disclaimer")}
    </div>
  );
}
