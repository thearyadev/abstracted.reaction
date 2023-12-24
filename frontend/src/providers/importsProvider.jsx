import React, { useState, useEffect } from "react";
import {devImportData} from "../data/devImportData.js";


export const ImportContext = React.createContext([]);

export const ImportsProvider = ({ children }) => {
  const [imports, setImports] = useState([]);
  useEffect(() => {
    const fetchImports = async () => {
      // do request
      setImports(devImportData);
    };
    fetchImports();
    const interval = setInterval(fetchImports, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ImportContext.Provider value={imports}>{children}</ImportContext.Provider>
  );
};
