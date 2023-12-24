import React, {Suspense} from 'react';
import {
    BrowserRouter as Router,
    Route,
    Switch,
    Redirect,
} from 'react-router-dom';
import {IntlProvider} from 'react-intl';

import AppLocale from './lang';
import ColorSwitcher from './components/common/ColorSwitcher.jsx';
import {NotificationContainer} from './components/common/react-notifications';
import {isMultiColorActive, adminRoot} from './constants/defaultValues';
import {getDirection} from './helpers/Utils';

import {FilmsProvider} from './providers/filmsProvider.jsx'
import {DiagnosticProvider} from "./providers/diagnosticProvider.jsx";
import {ActressesProvider} from "./providers/actressesProvider.jsx";
import {ImportsProvider} from "./providers/importsProvider.jsx";

const ViewApp = React.lazy(() =>
    import(/* webpackChunkName: "views-app" */ './views/app')
);

const ViewError = React.lazy(() =>
    import(/* webpackChunkName: "views-error" */ './views/error')
);

class App extends React.Component {

    constructor(props) {
        super(props);


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
                    locale={currentAppLocale.locale}
                    messages={currentAppLocale.messages}
                >
                    <FilmsProvider>
                        <DiagnosticProvider>
                            <ActressesProvider>
                                <ImportsProvider>
                                    <>
                                        <NotificationContainer/>
                                        {isMultiColorActive && <ColorSwitcher/>}
                                        <Suspense fallback={<div className="loading"/>}>
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

                                                    <Redirect exact from="/" to={`${adminRoot}/dashboard`}/>

                                                    <Redirect to="/error"/>

                                                    <Redirect to="/error"/>
                                                </Switch>
                                            </Router>
                                        </Suspense>
                                    </>
                                </ImportsProvider>
                            </ActressesProvider>
                        </DiagnosticProvider>
                    </FilmsProvider>

                </IntlProvider>
            </div>
        );
    }
}


export default App;