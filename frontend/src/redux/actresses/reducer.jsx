import { SET_ACTRESSES, FETCH_ACTRESSES_FAILURE, FETCH_ACTRESSES_REQUEST, FETCH_ACTRESSES_SUCCESS } from '../constants';

const INIT_STATE = {
  actresses: [],
  loading: false,
  error: null,
};


export default (state = INIT_STATE, action) => {
  switch (action.type) {
    case SET_ACTRESSES:
      return {
        ...state,
        actresses: action.payload,
      };
    case FETCH_ACTRESSES_REQUEST:
      return {
        ...state,
        loading: true,
        error: null,
      };
    case FETCH_ACTRESSES_SUCCESS:
      return {
        ...state,
        loading: false,
        actresses: action.payload,
      };
    case FETCH_ACTRESSES_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload,
      };
    default:
      return state;
  }
};

