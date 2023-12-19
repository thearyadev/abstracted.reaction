import React, { useState, useEffect } from "react";
import { devFilmData } from "../data/devFilmData.js";

export const FilmContext = React.createContext([]);

export const FilmsProvider = ({ children }) => {
  const [films, setFilms] = useState([]);
  useEffect(() => {
    const fetchFilms = async () => {
      // do request

      if (import.meta.env.DEV) {
        setFilms(devFilmData);
      } else {
        setFilms("Prod");
      }
    };
    fetchFilms();
    const interval = setInterval(fetchFilms, 3000);
    return () => clearInterval(interval);
  }, []);

  return <FilmContext.Provider value={films}>{children}</FilmContext.Provider>;
};
