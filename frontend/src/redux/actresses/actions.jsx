import { SET_ACTRESSES, FETCH_ACTRESSES_FAILURE, FETCH_ACTRESSES_REQUEST, FETCH_ACTRESSES_SUCCESS } from '../constants';

// eslint-disable-next-line import/prefer-default-export
export const setActresses = (actresses) => ({
  type: SET_ACTRESSES,
  payload: actresses,
});

export const fetchActressesRequest = () => ({
  type: FETCH_ACTRESSES_REQUEST,
});

export const fetchActressesSuccess = (actresses) => ({
  type: FETCH_ACTRESSES_SUCCESS,
  payload: actresses,
});

export const fetchActressesFailure = (error) => ({
  type: FETCH_ACTRESSES_FAILURE,
  payload: error,
});

export const fetchActresses = () => {
  return async (dispatch) => {
    dispatch(fetchActressesRequest());
    try{
      const response = await fetch("/api/actress_detail");
      const data = await response.json();
      dispatch(fetchActressesSuccess(data));
      dispatch(setActresses(data));
    }catch(error){
      dispatch(fetchActressesFailure(error.message));
    }
  }
}