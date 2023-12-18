import React, { useState, useEffect } from "react";

export const FilmContext = React.createContext([]);

export const FilmProvider = ({ children }) => {
  const [films, setFilms] = useState([]);
  useEffect(() => {
    const fetchFilms = async () => {
      // do request
      setFilms([]);
    };
    fetchFilms();
    const interval = setInterval(fetchFilms, 3000);
    return () => clearInterval(interval);
  }, []);

  return <FilmContext.Provider value={films}>{children}</FilmContext.Provider>;
};
