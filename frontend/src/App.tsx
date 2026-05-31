import { Route, Routes } from "react-router-dom";

import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { Nav } from "./components/Nav";
import { CaseDetailPage } from "./pages/CaseDetailPage";
import { CaseListPage } from "./pages/CaseListPage";
import { CoachingReportPage } from "./pages/CoachingReportPage";
import { DashboardPage } from "./pages/DashboardPage";
import { NewCasePage } from "./pages/NewCasePage";
import { StatutesPage } from "./pages/StatutesPage";
import { TrainingDashboardPage } from "./pages/TrainingDashboardPage";

export default function App() {
  return (
    <>
      <DisclaimerBanner />
      <Nav />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<TrainingDashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/cases" element={<CaseListPage />} />
          <Route path="/cases/new" element={<NewCasePage />} />
          <Route path="/cases/:id" element={<CaseDetailPage />} />
          <Route path="/training/:sessionId" element={<CoachingReportPage />} />
          <Route path="/statutes" element={<StatutesPage />} />
        </Routes>
      </main>
    </>
  );
}
