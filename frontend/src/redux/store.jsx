// import { createStore, applyMiddleware, compose } from 'redux';
// import createSagaMiddleware from 'redux-saga';
// import { composeWithDevTools } from 'redux-devtools-extension';
// import thunk from 'redux-thunk';
//
// import reducers from './reducers';
// import sagas from './sagas';
//
// const sagaMiddleware = createSagaMiddleware();
//
// const middlewares = [sagaMiddleware, thunk];
//
// // eslint-disable-next-line import/prefer-default-export
// export function configureStore(initialState) {
//   const store = createStore(
//     reducers,
//     initialState,
//     // compose(applyMiddleware(...middlewares), composeWithDevTools()),
//     compose(applyMiddleware(...middlewares)),
//     );
//
//   sagaMiddleware.run(sagas);
//
//   if (module.hot) {
//     module.hot.accept('./reducers', () => {
//       // eslint-disable-next-line global-require
//       const nextRootReducer = require('./reducers');
//       store.replaceReducer(nextRootReducer);
//     });
//   }
//
//   return store;
// }

import { createStore, applyMiddleware, compose } from 'redux';
import createSagaMiddleware from 'redux-saga';
import thunk from 'redux-thunk';
import reducers from './reducers';
import sagas from './sagas';

const sagaMiddleware = createSagaMiddleware();
const middlewares = [sagaMiddleware, thunk];

export function configureStore(initialState) {
  const store = createStore(
      reducers,
      initialState,
      compose(applyMiddleware(...middlewares)),
  );

  sagaMiddleware.run(sagas);

  // Vite-specific HMR code
  if (import.meta.hot) {
    import.meta.hot.accept('./reducers', (newReducers) => {
      store.replaceReducer(newReducers.default);
    });
  }

  return store;
}
