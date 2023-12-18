import { SET_FILMS, FETCH_FILMS_FAILURE, FETCH_FILMS_REQUEST, FETCH_FILMS_SUCCESS } from '../constants';

const INIT_STATE = {
  films: [],
  loading: false,
  error: null,
};


export default (state = INIT_STATE, action) => {
  switch (action.type) {
    case SET_FILMS:
      return {
        ...state,
        films: action.payload,
      };
    case FETCH_FILMS_REQUEST:
      return {
        ...state,
        loading: true,
        error: null,
      };
    case FETCH_FILMS_SUCCESS:
      return {
        ...state,
        loading: false,
        films: action.payload,
      };
    case FETCH_FILMS_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload,
      };
    default:
      return state;
  }
};

