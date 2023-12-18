import React, { Suspense } from 'react';
import { Route, withRouter, Switch } from 'react-router-dom';
import { connect } from 'react-redux';
import { useSelector } from 'react-redux';
import AppLayout from '../../layout/AppLayout';
import {useState, useEffect} from 'react';

const Films = React.lazy(() =>
  import('./films')
);
const Actresses = React.lazy(() =>
  import('./actresses')
);

const Dashboard = React.lazy(() =>
  import('./dashboard')
);

const Import = React.lazy( () =>
  import('./import/index.jsx')
);

const App = ({ match }) => {
  const films = useSelector((state) => state.films.films);
  const [showRoutes, setShowRoutes] = useState(false);

  useEffect(() => {
    // Show the routes after 2 seconds
    const timerId = setTimeout(() => {
      setShowRoutes(true);
    }, 1);

    // Clear the timer if the component is unmounted before it finishes
    return () => clearTimeout(timerId);
  }, []);

  return (
    <AppLayout>
      <div className="dashboard-wrapper">
        {showRoutes ? (
          <Suspense fallback={<div className="loading" />}>
            <Switch>
              {/* redirects / to /<endpoint> */}




              <Route
                path={`${match.url}/dashboard`}
                render={(props) => <Dashboard {...props} />}
              />
              <Route
                path={`${match.url}/films`}
                render={(props) => <Films {...props} />}
              />
              <Route
              path={`${match.url}/actresses`}
              render={(props) => <Actresses {...props} />}
              />
              <Route
                  path={`${match.url}/import`}
                  render={(props) => <Import {...props} /> }
              />




              {/* if no route is matched, go to error.  */}
            </Switch>
          </Suspense>
        ) : (
          <div className="loading" />
        )}
      </div>
    </AppLayout>
  );
};


const mapStateToProps = ({ menu }) => {
  const { containerClassnames } = menu;
  return { containerClassnames };
};

export default withRouter(connect(mapStateToProps, {})(App));
