import React, { Suspense } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from 'react-router-dom';
import { IntlProvider } from 'react-intl';

import AppLocale from './lang';
import ColorSwitcher from './components/common/ColorSwitcher.jsx';
import { NotificationContainer } from './components/common/react-notifications';
import { isMultiColorActive, adminRoot } from './constants/defaultValues';
import { getDirection } from './helpers/Utils';

import { FilmProvider } from './providers/filmProvider.jsx'

const ViewApp = React.lazy(() =>
  import(/* webpackChunkName: "views-app" */ './views/app')
);

const ViewError = React.lazy(() =>
  import(/* webpackChunkName: "views-error" */ './views/error')
);

class App extends React.Component {

  constructor(props) {
    super(props);
    const completed = false;


    const direction = getDirection();
    if (direction.isRtl) {
      document.body.classList.add('rtl');
      document.body.classList.remove('ltr');
    } else {
      document.body.classList.add('ltr');
      document.body.classList.remove('rtl');
    }
  }



  render() {
    const locale = "en"
    const currentAppLocale = AppLocale[locale];
    return (
      <div className="h-100">
        <IntlProvider
          locale={currentAppLocale.locale }
          messages={currentAppLocale.messages}
        >
          <FilmProvider>

              <>
                <NotificationContainer />
                {isMultiColorActive && <ColorSwitcher />}
                <Suspense fallback={<div className="loading" />}>
                  <Router>
                    <Switch>
                      <Route
                          path={adminRoot}
                          render={(props) => <ViewApp {...props} />}
                      />
                      <Route
                          path="/error"
                          exact
                          render={(props) => <ViewError {...props} />}
                      />
                      {/* redirects / to films page */}

                      <Redirect exact from="/" to={`${adminRoot}/accueil`} />

                      <Redirect to="/error" />

                      <Redirect to="/error" />
                    </Switch>
                  </Router>
                </Suspense>
              </>
          </FilmProvider>

        </IntlProvider>
      </div>
    );
  }
}


export default App;
