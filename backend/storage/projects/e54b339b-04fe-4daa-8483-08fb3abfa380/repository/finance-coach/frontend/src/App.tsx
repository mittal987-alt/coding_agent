import { Routes, Route } from "react-router-dom";
import { FinanceProvider } from "./context/FinanceContext";
import Layout from "./components/Layout";

import Overview from "./pages/Overview";
import DailyBrief from "./pages/DailyBrief";
import Notifications from "./pages/Notifications";
import Goals from "./pages/Goals";
import Subscriptions from "./pages/Subscriptions";
import Accounts from "./pages/Accounts";
import Calendar from "./pages/Calendar";
import Splits from "./pages/Splits";
import Tax from "./pages/Tax";
import Planner from "./pages/Planner";
import Achievements from "./pages/Achievements";
import RecurringTransactions from "./pages/RecurringTransactions";
import Investments from "./pages/Investments";
import Loans from "./pages/Loans";
import Settings from "./pages/settings";
import Challenges from "./pages/Challenges";

function App() {
  return (
    <FinanceProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/"              element={<Overview />} />
          <Route path="/daily-brief"   element={<DailyBrief />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/goals"         element={<Goals />} />
          <Route path="/subscriptions" element={<Subscriptions />} />
          <Route path="/accounts"      element={<Accounts />} />
          <Route path="/calendar"      element={<Calendar />} />
          <Route path="/splits"        element={<Splits />} />
          <Route path="/tax"           element={<Tax />} />
          <Route path="/planner"       element={<Planner />} />
          <Route path="/achievements"  element={<Achievements />} />
          <Route path="/recurring"     element={<RecurringTransactions />} />
          <Route path="/investments"   element={<Investments />} />
          <Route path="/loans"         element={<Loans />} />
          <Route path="/settings"      element={<Settings />} />
          <Route path="/challenges"    element={<Challenges />} />
        </Route>
      </Routes>
    </FinanceProvider>
  );
}

export default App;
