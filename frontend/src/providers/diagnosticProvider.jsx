import React, { useState, useEffect } from "react";
import { devDiagnosticData } from "../data/devDiagnosticData.js";

const diagnostic_default_state = {};

export const DiagnosticContext = React.createContext(diagnostic_default_state);

export const DiagnosticProvider = ({ children }) => {
  const [diagnostics, setDiagnostics] = useState(diagnostic_default_state);

  useEffect(() => {
    const fetchDiagnostics = async () => {
      // do request
      if (import.meta.env.DEV) {
        setDiagnostics(devDiagnosticData);
      }
    };
    fetchDiagnostics();
    const interval = setInterval(fetchDiagnostics, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DiagnosticContext.Provider value={diagnostics}>
      {children}
    </DiagnosticContext.Provider>
  );
};
