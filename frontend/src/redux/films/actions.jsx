import { SET_FILMS, FETCH_FILMS_FAILURE, FETCH_FILMS_REQUEST, FETCH_FILMS_SUCCESS } from '../constants';

// eslint-disable-next-line import/prefer-default-export
export const setFilms = (films) => ({
  type: SET_FILMS,
  payload: films,
});

export const fetchFilmsFailure = (error) => ({
  type: FETCH_FILMS_FAILURE,
  payload: error,
});

export const fetchFilmsRequest = () => ({
  type: FETCH_FILMS_REQUEST,
})
export const fetchFilmsSuccess = (films) => ({
  type: FETCH_FILMS_SUCCESS,
  payload: films,
});


export const fetchFilms = () => {
  return async (dispatch) => {
    dispatch(fetchFilmsRequest());
    try{
      const response = await fetch("/api/films");
      const data = await response.json();
      dispatch(fetchFilmsSuccess(data));
      dispatch(setFilms(data));
    }catch(error){
      dispatch(fetchFilmsFailure(error.message));
    }
  }
}