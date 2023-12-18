import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

const FilmList = React.lazy(() =>
  import(/* webpackChunkName: "start" */ './film_list.jsx')
);

const FilmsHandler = ({ match }) => (
  <Suspense fallback={<div className="loading" />}>
    <Switch>
      <Route
        path={`${match.url}`}
        render={(props) => <FilmList {...props} />}
      />
      <Redirect to="/error" />
    </Switch>
  </Suspense>
);
export default FilmsHandler;
