import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

const Start = React.lazy(() =>
  import(/* webpackChunkName: "second" */ './start')
);

const ActressDetail = React.lazy(() => 
  import(/* webpackChunkName: "actress-details" */ './actress_detail')
);
const Actrices = ({ match }) => {
  return (
    <Suspense fallback={<div className="loading" />}>
      <Switch>
        <Route
          path={`${match.url}`}
          render={(props) => <Start {...props} />}
        />

        {/*<Route*/}
        {/*  path={`${match.url}/:actrice`}*/}
        {/*  render={(props) => <ActressDetail {...props } actress={props.match.params.actrice} />}*/}
        {/*  />        */}
        <Redirect to="/error" />
      </Switch>
    </Suspense>
  )
};
export default Actrices;
