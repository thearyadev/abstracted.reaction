import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';


const Dashboard = React.lazy(() =>
    import(/* webpackChunkName: "start" */ './dashboard')
);


const DashboardHandler = ({ match }) => (
  <Suspense fallback={<div className="loading" />}>
    <Switch>
      <Route
        path={`${match.url}`}
        render={(props) => <Dashboard {...props} />}
      />
      <Redirect to="/error" />
    </Switch>
  </Suspense>
);
export default DashboardHandler;
