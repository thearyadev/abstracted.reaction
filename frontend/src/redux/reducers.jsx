import { combineReducers } from 'redux';
import settings from './settings/reducer';
import menu from './menu/reducer';
import actresses from './actresses/reducer';
import films from './films/reducer';

const reducers = combineReducers({
  menu,
  settings,
  actresses,
  films
});

export default reducers;
