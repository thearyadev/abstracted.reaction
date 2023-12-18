import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

const Start = React.lazy(() =>
  import(/* webpackChunkName: "start" */ './start')
);

const Player = React.lazy(() =>
  import(/* webpackChunkName: "start" */ './player')
);

const Cinema = ({ match }) => (
  <Suspense fallback={<div className="loading" />}>
    <Switch>
      {/*<Route*/}
      {/*  path={`${match.url}/cinémathèque/:uuid`}*/}
      {/*  render={(props) => <Player {...props} uuid={props.match.params.uuid} />}*/}
      {/*/>*/}
      <Route
        path={`${match.url}`}
        render={(props) => <Start {...props} />}
      />
      {/* add another route here for the player  */}
      <Redirect to="/error" />
    </Switch>
  </Suspense>
);
export default Cinema;
