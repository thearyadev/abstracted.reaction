import React, { Suspense } from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

const ActressList = React.lazy(() =>
  import(/* webpackChunkName: "second" */ './actress_list.jsx')
);

const ActressDetail = React.lazy(() =>
    import("./actress_detail.jsx")
);

const ActressHandler = ({ match }) => {
  return (
    <Suspense fallback={<div className="loading" />}>
      <Switch>

          <Route
              path={`${match.url}/:actress`}
              render={(props) => <ActressDetail {...props } actress={props.match.params.actress} />}

          />
          <Route
          path={`${match.url}`}
          render={(props) => <ActressList {...props} />}
        />

        <Redirect to="/error" />
      </Switch>
    </Suspense>
  )
};
export default ActressHandler;
