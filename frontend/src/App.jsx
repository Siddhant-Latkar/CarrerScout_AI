
import { useEffect, useState } from "react";

import { getHealth } from "./api/health";

function App() {
  const [apiStatus, setApiStatus] = useState("checking...");

  useEffect(() => {
    let ignore = false;

    getHealth()
      .then((data) => {
        if (!ignore) setApiStatus(data.status);
      })
      .catch(() => {
        if (!ignore) setApiStatus("unreachable");
      });

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center gap-3">
      <h1 className="text-4xl font-bold">CareerScout AI</h1>
      <p className="text-slate-300">
        Backend status: <span className="font-semibold">{apiStatus}</span>
      </p>
    </main>
  );
}

export default App;
