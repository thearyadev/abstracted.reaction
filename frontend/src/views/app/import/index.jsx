import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';


const Import = React.lazy(() =>
    import(/* webpackChunkName: "start" */ './import')
);


const ImportHandler = ({ match }) => (
  <Suspense fallback={<div className="loading" />}>
    <Switch>
      <Route
        path={`${match.url}`}
        render={(props) => <Import {...props} />}
      />
      <Redirect to="/error" />
    </Switch>
  </Suspense>
);
export default ImportHandler;
