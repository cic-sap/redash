from flask import make_response
from flask_restful import Api
from werkzeug.wrappers import Response

from redash.handlers.alerts import (
    AlertListResource,
    AlertResource,
    AlertMuteResource,
    AlertSubscriptionListResource,
    AlertSubscriptionResource,
)
from redash.handlers.base import org_scoped_rule
from redash.handlers.dashboards import (
    MyDashboardsResource,
    DashboardFavoriteListResource,
    DashboardListResource,
    DashboardResource,
    DashboardShareResource,
    DashboardEmailResource,
    DashboardTagsResource,
    PublicDashboardResource,
)
from redash.handlers.data_sources import (
    DataSourceListResource,
    DataSourcePauseResource,
    DataSourceResource,
    DataSourceSchemaResource,
    DataSourceTestResource,
    DataSourceTypeListResource,
)
from redash.handlers.databricks import (
    DatabricksDatabaseListResource,
    DatabricksSchemaResource,
    DatabricksTableColumnListResource,
)
from redash.handlers.destinations import (
    DestinationListResource,
    DestinationResource,
    DestinationTypeListResource,
)
from redash.handlers.events import EventsResource
from redash.handlers.favorites import DashboardFavoriteResource, QueryFavoriteResource
from redash.handlers.groups import (
    GroupDataSourceListResource,
    GroupDataSourceResource,
    GroupListResource,
    GroupMemberListResource,
    GroupMemberResource,
    GroupResource,
)
from redash.handlers.permissions import (
    CheckPermissionResource,
    ObjectPermissionsListResource,
)
from redash.handlers.queries import (
    MyQueriesResource,
    QueryArchiveResource,
    QueryFavoriteListResource,
    QueryForkResource,
    QueryListResource,
    QueryRecentResource,
    QueryRefreshResource,
    QueryResource,
    QuerySearchResource,
    QueryTagsResource,
    QueryRegenerateApiKeyResource,
)
from redash.handlers.query_results import (
    JobResource,
    QueryResultDropdownResource,
    QueryDropdownsResource,
    QueryResultListResource,
    QueryResultResource,
)
from redash.handlers.query_snippets import (
    QuerySnippetListResource,
    QuerySnippetResource,
)
from redash.handlers.settings import OrganizationSettings
from redash.handlers.subscribe import EmailSubscriptionResource
from redash.handlers.users import (
    UserDisableResource,
    UserInviteResource,
    UserListResource,
    UserRegenerateApiKeyResource,
    UserResetPasswordResource,
    UserResource,
)
from redash.handlers.visualizations import (
    VisualizationListResource,
    VisualizationResource,
)
from redash.handlers.widgets import WidgetListResource, WidgetResource
from redash.utils import json_dumps


class ApiExt(Api):
    def add_org_resource(self, resource, *urls, **kwargs):
        urls = [org_scoped_rule(url) for url in urls]
        return self.add_resource(resource, *urls, **kwargs)


api = ApiExt()


@api.representation("application/json")
def json_representation(data, code, headers=None):
    # Flask-Restful checks only for flask.Response but flask-login uses werkzeug.wrappers.Response
    if isinstance(data, Response):
        return data
    resp = make_response(json_dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


api.add_org_resource(AlertResource, "/api/alerts/<alert_id>", endpoint="alert")
api.add_org_resource(
    AlertMuteResource, "/api/alerts/<alert_id>/mute", endpoint="alert_mute"
)
api.add_org_resource(
    AlertSubscriptionListResource,
    "/api/alerts/<alert_id>/subscriptions",
    endpoint="alert_subscriptions",
)
api.add_org_resource(
    AlertSubscriptionResource,
    "/api/alerts/<alert_id>/subscriptions/<subscriber_id>",
    endpoint="alert_subscription",
)
'''

curl -v  'http://localhost:8080/api/email-subscription/1' \
  -X 'POST' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 0' \
  -H 'sec-ch-ua: "Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'DNT: 1' \
  -H 'X-CSRF-TOKEN: ImIxYmRjMTc0OGYzYjEwZTU2YTc3YjM1ZjgxZWQ5YmYyN2RjMGJlYzMi.YYIeyg.-PLsMcMFyo0lg7Rww8dwPIw7bFU' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'Origin: http://localhost:8080' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: http://localhost:8080/dashboards/1-test1' \
  -H 'Accept-Language: en,zh-CN;q=0.9,zh;q=0.8' \
  -H 'Cookie: metabase.DEVICE=100e43d3-649c-4280-8d8b-72527c6bfad1; _ga=GA1.1.295563659.1634353309; metabase.SESSION=ee4885e4-a660-4e17-bfce-2b1a1005d088; remember_token=1-10f0557b308d87ea645e1e7fffba7a08|f9b050ca37acbaa00d40dc76465378d98c90f3b9e5fcbb18dd0ef9613e71c85c6794311b2225aaf4e5b08224fd8ea71ebe97a6521a77361f1eca35cb7b59b393; csrf_token=ImIxYmRjMTc0OGYzYjEwZTU2YTc3YjM1ZjgxZWQ5YmYyN2RjMGJlYzMi.YYIeyg.-PLsMcMFyo0lg7Rww8dwPIw7bFU; session=.eJw1z0tqA0EMRdG91DgBqX6SvJmmVJJICOmE7vbIZO8pMJ5fHuc90haHnx_pdh13f0vbp6VbKj0EhdhQBFXcWRyigGolRpMOUpmmYCjoiBwhnmU1UkQDOw2qMqP14gLsVc1KNO5qPgpS7rM3QotRJhMr1RyQG4QNVZ2lpwX59eN77L5fL9o8j9iuny_fl1BRbSJVjqII3vog0tKC0W0RMtkE9VnW0v3043kL3xECWlslsDH56LU5OkWEDhrA6e8fhC9Pxg.YYIeyg.5c_3BQdSLmTO9sbDXwSdq0WQwVs' \
  --compressed -d '{"email_list":"dongming.shen@sap.com"}'

curl -X POST 'http://localhost:8080/api/email-subscription/1' \
  -H 'Connection: keep-alive' \
  -H 'sec-ch-ua: "Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'DNT: 1' \
  -H 'X-CSRF-TOKEN: ImIxYmRjMTc0OGYzYjEwZTU2YTc3YjM1ZjgxZWQ5YmYyN2RjMGJlYzMi.YYIcZw.f2nigncW9QFcbF-18p46_V5g56k' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: http://localhost:8080/dashboards/1-test1' \
  -H 'Accept-Language: en,zh-CN;q=0.9,zh;q=0.8' \
  -H 'Cookie: metabase.DEVICE=100e43d3-649c-4280-8d8b-72527c6bfad1; _ga=GA1.1.295563659.1634353309; metabase.SESSION=ee4885e4-a660-4e17-bfce-2b1a1005d088; remember_token=1-10f0557b308d87ea645e1e7fffba7a08|f9b050ca37acbaa00d40dc76465378d98c90f3b9e5fcbb18dd0ef9613e71c85c6794311b2225aaf4e5b08224fd8ea71ebe97a6521a77361f1eca35cb7b59b393; csrf_token=ImIxYmRjMTc0OGYzYjEwZTU2YTc3YjM1ZjgxZWQ5YmYyN2RjMGJlYzMi.YYIcZw.f2nigncW9QFcbF-18p46_V5g56k; session=.eJw1z0tqA0EMRdG91DgBqX6SvJmmVJJICOmE7vbIZO8pMJ5fHuc90haHnx_pdh13f0vbp6VbKj0EhdhQBFXcWRyigGolRpMOUpmmYCjoiBwhnmU1UkQDOw2qMqP14gLsVc1KNO5qPgpS7rM3QotRJhMr1RyQG4QNVZ2lpwX59eN77L5fL9o8j9iuny_fl1BRbSJVjqII3vog0tKC0W0RMtkE9VnW0v3043kL3xECWlslsDH56LU5OkWEDhrA6e8fhC9Pxg.YYIcZw.aN2igqWxezSPUP7-mWrZEqT5Nt4' \
  --compressed -d '{"email_list":"dongming.shen@sap.com"}'

  '''
api.add_org_resource(AlertListResource, "/api/alerts", endpoint="alerts")

api.add_org_resource(EmailSubscriptionResource, "/api/email-subscription/<dashboard_id>", endpoint="email-subscription")
api.add_org_resource(DashboardListResource, "/api/dashboards", endpoint="dashboards")
api.add_org_resource(
    DashboardResource, "/api/dashboards/<dashboard_id>", endpoint="dashboard"
)
api.add_org_resource(
    PublicDashboardResource,
    "/api/dashboards/public/<token>",
    endpoint="public_dashboard",
)
api.add_org_resource(
    DashboardShareResource,
    "/api/dashboards/<dashboard_id>/share",
    endpoint="dashboard_share",
)
api.add_org_resource(
    DashboardEmailResource,
    "/api/dashboards/<dashboard_id>/email",
    endpoint="dashboard_email",
)

api.add_org_resource(
    DataSourceTypeListResource, "/api/data_sources/types", endpoint="data_source_types"
)
api.add_org_resource(
    DataSourceListResource, "/api/data_sources", endpoint="data_sources"
)
api.add_org_resource(
    DataSourceSchemaResource, "/api/data_sources/<data_source_id>/schema"
)
api.add_org_resource(
    DatabricksDatabaseListResource, "/api/databricks/databases/<data_source_id>"
)
api.add_org_resource(
    DatabricksSchemaResource,
    "/api/databricks/databases/<data_source_id>/<database_name>/tables",
)
api.add_org_resource(
    DatabricksTableColumnListResource,
    "/api/databricks/databases/<data_source_id>/<database_name>/columns/<table_name>",
)
api.add_org_resource(
    DataSourcePauseResource, "/api/data_sources/<data_source_id>/pause"
)
api.add_org_resource(DataSourceTestResource, "/api/data_sources/<data_source_id>/test")
api.add_org_resource(
    DataSourceResource, "/api/data_sources/<data_source_id>", endpoint="data_source"
)

api.add_org_resource(GroupListResource, "/api/groups", endpoint="groups")
api.add_org_resource(GroupResource, "/api/groups/<group_id>", endpoint="group")
api.add_org_resource(
    GroupMemberListResource, "/api/groups/<group_id>/members", endpoint="group_members"
)
api.add_org_resource(
    GroupMemberResource,
    "/api/groups/<group_id>/members/<user_id>",
    endpoint="group_member",
)
api.add_org_resource(
    GroupDataSourceListResource,
    "/api/groups/<group_id>/data_sources",
    endpoint="group_data_sources",
)
api.add_org_resource(
    GroupDataSourceResource,
    "/api/groups/<group_id>/data_sources/<data_source_id>",
    endpoint="group_data_source",
)

api.add_org_resource(EventsResource, "/api/events", endpoint="events")

api.add_org_resource(
    QueryFavoriteListResource, "/api/queries/favorites", endpoint="query_favorites"
)
api.add_org_resource(
    QueryFavoriteResource, "/api/queries/<query_id>/favorite", endpoint="query_favorite"
)
api.add_org_resource(
    DashboardFavoriteListResource,
    "/api/dashboards/favorites",
    endpoint="dashboard_favorites",
)
api.add_org_resource(
    DashboardFavoriteResource,
    "/api/dashboards/<object_id>/favorite",
    endpoint="dashboard_favorite",
)

api.add_org_resource(MyDashboardsResource, "/api/dashboards/my", endpoint="my_dashboards")

api.add_org_resource(QueryTagsResource, "/api/queries/tags", endpoint="query_tags")
api.add_org_resource(
    DashboardTagsResource, "/api/dashboards/tags", endpoint="dashboard_tags"
)

api.add_org_resource(
    QuerySearchResource, "/api/queries/search", endpoint="queries_search"
)
api.add_org_resource(
    QueryRecentResource, "/api/queries/recent", endpoint="recent_queries"
)
api.add_org_resource(
    QueryArchiveResource, "/api/queries/archive", endpoint="queries_archive"
)
api.add_org_resource(QueryListResource, "/api/queries", endpoint="queries")
api.add_org_resource(MyQueriesResource, "/api/queries/my", endpoint="my_queries")
api.add_org_resource(
    QueryRefreshResource, "/api/queries/<query_id>/refresh", endpoint="query_refresh"
)
api.add_org_resource(QueryResource, "/api/queries/<query_id>", endpoint="query")
api.add_org_resource(
    QueryForkResource, "/api/queries/<query_id>/fork", endpoint="query_fork"
)
api.add_org_resource(
    QueryRegenerateApiKeyResource,
    "/api/queries/<query_id>/regenerate_api_key",
    endpoint="query_regenerate_api_key",
)

api.add_org_resource(
    ObjectPermissionsListResource,
    "/api/<object_type>/<object_id>/acl",
    endpoint="object_permissions",
)
api.add_org_resource(
    CheckPermissionResource,
    "/api/<object_type>/<object_id>/acl/<access_type>",
    endpoint="check_permissions",
)

api.add_org_resource(
    QueryResultListResource, "/api/query_results", endpoint="query_results"
)
api.add_org_resource(
    QueryResultDropdownResource,
    "/api/queries/<query_id>/dropdown",
    endpoint="query_result_dropdown",
)
api.add_org_resource(
    QueryDropdownsResource,
    "/api/queries/<query_id>/dropdowns/<dropdown_query_id>",
    endpoint="query_result_dropdowns",
)
api.add_org_resource(
    QueryResultResource,
    "/api/query_results/<query_result_id>.<filetype>",
    "/api/query_results/<query_result_id>",
    "/api/queries/<query_id>/results",
    "/api/queries/<query_id>/results.<filetype>",
    "/api/queries/<query_id>/results/<query_result_id>.<filetype>",
    endpoint="query_result",
)
api.add_org_resource(
    JobResource,
    "/api/jobs/<job_id>",
    "/api/queries/<query_id>/jobs/<job_id>",
    endpoint="job",
)

api.add_org_resource(UserListResource, "/api/users", endpoint="users")
api.add_org_resource(UserResource, "/api/users/<user_id>", endpoint="user")
api.add_org_resource(
    UserInviteResource, "/api/users/<user_id>/invite", endpoint="user_invite"
)
api.add_org_resource(
    UserResetPasswordResource,
    "/api/users/<user_id>/reset_password",
    endpoint="user_reset_password",
)
api.add_org_resource(
    UserRegenerateApiKeyResource,
    "/api/users/<user_id>/regenerate_api_key",
    endpoint="user_regenerate_api_key",
)
api.add_org_resource(
    UserDisableResource, "/api/users/<user_id>/disable", endpoint="user_disable"
)

api.add_org_resource(
    VisualizationListResource, "/api/visualizations", endpoint="visualizations"
)
api.add_org_resource(
    VisualizationResource,
    "/api/visualizations/<visualization_id>",
    endpoint="visualization",
)

api.add_org_resource(WidgetListResource, "/api/widgets", endpoint="widgets")
api.add_org_resource(WidgetResource, "/api/widgets/<int:widget_id>", endpoint="widget")

api.add_org_resource(
    DestinationTypeListResource, "/api/destinations/types", endpoint="destination_types"
)
api.add_org_resource(
    DestinationResource, "/api/destinations/<destination_id>", endpoint="destination"
)
api.add_org_resource(
    DestinationListResource, "/api/destinations", endpoint="destinations"
)

api.add_org_resource(
    QuerySnippetResource, "/api/query_snippets/<snippet_id>", endpoint="query_snippet"
)
api.add_org_resource(
    QuerySnippetListResource, "/api/query_snippets", endpoint="query_snippets"
)

api.add_org_resource(
    OrganizationSettings, "/api/settings/organization", endpoint="organization_settings"
)
