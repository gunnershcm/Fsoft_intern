# import geopy.distance
import math
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
from xml.dom import ValidationErr
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountAssetAuditDetail(models.Model):
    _name = "account.asset.audit.detail"
    _description = "Asset/Asset audit detail"
    
    ticket_id = fields.Many2one("account.asset.audit.ticket", string="Ticket code")
    asset_detail_id = fields.Many2one("account.asset.detail", string="Asset Detail", required=True)
    status = fields.Many2one("account.asset.detail.status", string="Status")

    location_type_system = fields.Selection(
        [("warehouse", "Warehouse"), ("customer", "Customer")],
        string="(S) Loc type",
        copy=False,
        default="warehouse",
    )
    location_type_audit = fields.Selection(
        [("warehouse", "Warehouse"), ("customer", "Customer")],
        string="(A) Loc type",
        copy=False,
        default="warehouse",
    )
    location_system = fields.Char(string="(S) Location")
    location_audit = fields.Char(string="(A) Location")
    latitude_system = fields.Float(string="(S) Lat", digits=(3, 4))
    latitude_audit = fields.Float(string="(A) Lat", digits=(3, 4))
    longitude_system = fields.Float(string="(S) Lon", digits=(3, 4))
    longitude_audit = fields.Float(string="(A) Lon", digits=(3, 4))
    has_gap = fields.Char(string="Gap?", compute="_compute_gap", default="No")
    gap_distance = fields.Float(
        string="Distance (m)",
        digits=(9, 4),
        compute="_compute_gap_distance",
        store=True,
    )
    # auditor = fields.Char(string='Auditor', required=True)
    audit_time = fields.Datetime(string="Audit time", required=True)
    image = fields.Image(string="Image", max_width=128, max_height=128)

    @api.model
    @api.onchange(
        "latitude_system", "latitude_audit", "longitude_system", "longitude_audit"
    )
    def _check_values(self):
        error = False
        if self.latitude_system < -90.0 or self.latitude_system > 90.0:
            error = True
        if self.latitude_audit < -90.0 or self.latitude_audit > 90.0:
            error = True
        if self.longitude_system < -180.0 or self.longitude_system > 180.0:
            error = True
        if self.longitude_audit < -180.0 or self.longitude_audit > 180.0:
            error = True
        if error == True:
            raise ValidationError(
                _("Latitudes are in [-90.0, 900.0] degrees and Longitudes are in [-180.0, 180.0]!")
            )

    @api.depends(
        "latitude_system", "latitude_audit", "longitude_system", "longitude_audit"
    )
    def _compute_gap(self):
        # import wdb; wdb.set_trace()
        for asset_item in self:
            asset_item.has_gap = (
                "No" if math.isclose(asset_item.gap_distance, 0) == True else "Yes"
            )
        

    @api.depends("latitude_system", "latitude_audit", "longitude_system", "longitude_audit")
    def _compute_gap_distance(self):    
        for asset_item in self:  #
            coords_system = (asset_item.latitude_system, asset_item.longitude_system)
            coords_audit = (asset_item.latitude_audit, asset_item.longitude_audit)
            # lat_diff = asset_item.latitude_system - asset_item.latitude_audit
            # long_diff = asset_item.longitude_system - asset_item.longitude_audit
            # asset_item.gap_distance = math.sqrt(lat_diff ** 2 + long_diff ** 2)

            # geopy.distance.geodesic(coords_1, coords_2).km
            asset_item.gap_distance = self.find_distance(coords_system, coords_audit)


    # Haversine formula
    def find_distance(self, c1=(0, 0), c2=(0, 0)):
        # approximate radius of earth in km
        R = 6373.0

        lat1, lon1 = c1
        lat2, lon2 = c2
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
