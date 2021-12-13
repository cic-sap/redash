import time

from flask import request, url_for
from funcy import project

from redash import models
from redash.serializers import serialize_alert
from redash.handlers.base import BaseResource, get_object_or_404, require_fields
from redash.permissions import (
    require_access,
    require_admin_or_owner,
    require_permission,
    view_only,
)
from redash.utils import json_dumps


class EmailSubscriptionResource(BaseResource):

    def get(self, dashboard_id):
        #return {'hello':'world'}
        return self.post(dashboard_id)

    def post(self, dashboard_id):
        # req = request.get_json(True)
        # print("EmailSubscriptionResource get req",req,"dashboard_id:",dashboard_id)

        kwargs = {"user": self.current_user, "dashboard_id": dashboard_id}
        kwargs["email_list"]="dongming.shen@sap.com"
        # todo query params
        # if "email_list" in req:
        #     kwargs["email_list"] = req["email_list"]

        if request.args.get("legacy") is not None:
            fn = models.Dashboard.get_by_slug_and_org
        else:
            fn = models.Dashboard.get_by_id_and_org

        dashboard = get_object_or_404(fn, dashboard_id, self.current_org)

        api_key = models.ApiKey.get_by_object(dashboard)
        if not api_key:
            return {}

        public_url = url_for(
            "redash.public_dashboard",
            token=api_key.api_key,
            org_slug=self.current_org.slug,
            _external=True,
        )
        print("public_url",public_url,'email',kwargs["email_list"])

        return {'public_url': public_url}

