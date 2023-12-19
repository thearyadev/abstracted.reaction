import React, { useState, useEffect } from "react";
import { devActressesData } from "../data/devActressesData.js";

export const ActressesContext = React.createContext([]);

export const ActressesProvider = ({ children }) => {
  const [actresses, setActresses] = useState([]);
  useEffect(() => {
    const fetchActresses = async () => {
      // do request
      if (import.meta.env.DEV) {
        setActresses(devActressesData);
      }
    };
    fetchActresses();
    const interval = setInterval(fetchActresses, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ActressesContext.Provider value={actresses}>
      {children}
    </ActressesContext.Provider>
  );
};
