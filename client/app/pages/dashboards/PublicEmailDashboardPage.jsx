import {isEmpty} from "lodash";
import React from "react";
import PropTypes from "prop-types";

import routeWithApiKeySession from "@/components/ApplicationArea/routeWithApiKeySession";
import Link from "@/components/Link";
import BigMessage from "@/components/BigMessage";
import PageHeader from "@/components/PageHeader";
import Parameters from "@/components/Parameters";
// import DashboardGrid from "@/components/dashboards/DashboardGrid";
import EmailDashboardGrid from "@/components/dashboards/EmailDashboardGrid";
import Filters from "@/components/Filters";

import {Dashboard} from "@/services/dashboard";
import routes from "@/services/routes";

import logoUrl from "@/assets/images/redash_icon_small.png";

import useDashboard from "./hooks/useDashboard";

import "./PublicDashboardPage.less";

function PublicEmailDashboard({dashboard}) {
  const {globalParameters, filters, setFilters, refreshDashboard, loadWidget, refreshWidget} = useDashboard(
    dashboard
  );

  return (
    <div className="container p-t-10 p-b-20">

      <table style={{'width': '100%', height: '100%'}}>
        <tr>
          <td valign={"top"} align={"center"}>

            <table style={{width: '900px'}}>
              <tr>
                <td align={"left"}>
                  <h3 style={{'textAlign': 'left'}}>{dashboard.name}</h3>
                </td>
              </tr>
            {!isEmpty(globalParameters) && (
              <tr>
                <td align={"left"}>
                  <p style={{clean:'both','textAlign':'left'}}>
                    <Parameters parameters={globalParameters} onValuesChange={refreshDashboard}/>
                  </p>
                  </td>
              </tr>
            )}
                 {!isEmpty(filters) && (
              <tr>
                <td align={"left"}>
                    <div className="m-b-10 p-15 bg-white tiled">
                      <Filters filters={filters} onChange={setFilters}/>
                    </div>
                   </td>
              </tr>
            )}

            </table>



            <div>
              <EmailDashboardGrid
                dashboard={dashboard}
                widgets={dashboard.widgets}
                filters={filters}
                isEditing={false}
                isPublic
                onLoadWidget={loadWidget}
                onRefreshWidget={refreshWidget}
              />
            </div>
          </td>
        </tr>
      </table>
    </div>
  );
}

PublicEmailDashboard.propTypes = {
  dashboard: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

class PublicEmailDashboardPage extends React.Component {
  static propTypes = {
    token: PropTypes.string.isRequired,
    onError: PropTypes.func,
  };

  static defaultProps = {
    onError: () => {
    },
  };

  state = {
    loading: true,
    dashboard: null,
  };

  componentDidMount() {
    Dashboard.getByToken({token: this.props.token})
      .then(dashboard => this.setState({dashboard, loading: false}))
      .catch(error => this.props.onError(error));
  }

  render() {
    const {loading, dashboard} = this.state;
    return (
      <div className="public-dashboard-page">
        {loading ? (
          <div className="container loading-message">
            <BigMessage className="" icon="fa-spinner fa-2x fa-pulse" message="Loading..."/>
          </div>
        ) : (
          <PublicEmailDashboard dashboard={dashboard}/>
        )}
        <div id="footer">
          <div className="text-center">
            <Link href="https://redash.io">
              <img alt="Redash Logo" src={logoUrl} width="38"/>
            </Link>
          </div>
          Powered by <Link href="https://redash.io/?ref=public-dashboard">Redash</Link>
        </div>
      </div>
    );
  }
}

routes.register(
  "Dashboards.ViewEmailShared",
  routeWithApiKeySession({
    path: "/public/email-dashboards/:token",
    render: pageProps => <PublicEmailDashboardPage {...pageProps} />,
    getApiKey: currentRoute => currentRoute.routeParams.token,
  })
);
