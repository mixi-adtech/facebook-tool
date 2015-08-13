from app.common.config import Config
from facebookads.api import FacebookAdsApi
from facebookads.objects import (
    AdAccount,
    AdSet,
    AdCampaign,
    CustomAudience
)

import pprint

COUNTRY_CODES = ['JP', 'US', 'CA', 'TW', 'HK', 'MO', 'KR']
AGE_RANGE = range(13, 66)
pp = pprint.PrettyPrinter(indent=4)
config = Config().get_config()

FacebookAdsApi.init(
    config['api_app_id'],
    config['app_secret'],
    config['access_token'],
)


class AdSetModel:
    def __init__(self, act_id):
        self.act_id = act_id

    def get_ad_set(self):
        account = AdAccount(self.act_id)
        adsets = account.get_ad_sets(
            fields=[
                AdSet.Field.name,
                AdSet.Field.status,
                AdSet.Field.campaign_group_id
            ],
            params={
                'campaign_status': ['ACTIVE'],
                'limit': 100
            }
        )

        campaigns = account.get_ad_campaigns(
            fields=[
                AdCampaign.Field.name,
                AdCampaign.Field.status
            ],
            params={
                'campaign_group_status': ['ACTIVE']
            }
        )

        ads = []
        for adset in adsets:
            for i in range(0, len(campaigns)):
                campaign = campaigns[i]
                if adset['campaign_group_id'] == campaign['id']:
                    ads.append({
                        'id': adset['id'],
                        'name': adset['name'],
                        'campaign_name': campaign['name']
                    })
                    break
        return sorted(ads, key=lambda ad: ad['campaign_name'] + ad['name'])


class SelectTarget:
    def __init__(self, param):
        self.param = param

    def select_target(self):
        parent_id = config['act_id'][self.param['account']]
        account = AdAccount(parent_id)
        campaigns = account.get_ad_campaigns(
            fields=[
                AdCampaign.Field.name,
                AdCampaign.Field.status
            ],
            params={
                'campaign_group_status': ['ACTIVE']
            }
        )

        adset = AdSet(self.param['adset_id'])
        adset.remote_read(
            fields=[
                AdSet.Field.name,
                AdSet.Field.targeting,
                AdSet.Field.campaign_group_id,
            ]
        )
        # pp.pprint(adset)

        if(('genders' in adset['targeting']) and
                (len(adset['targeting']['genders']) == 1)):
            gender = adset['targeting']['genders'][0]
        else:
            gender = 0

        for i in range(0, len(campaigns)):
            campaign = campaigns[i]
            if adset['campaign_group_id'] == campaign['id']:
                campaign_name = campaign['name']
                break

        country_list = []
        for country in COUNTRY_CODES:
            is_checked = 0
            if (country in adset['targeting']['geo_locations']['countries']):
                is_checked = 1

            countries = {
                'name': country,
                'is_checked': is_checked
            }
            country_list.append(countries)

        custom_audiences = account.get_custom_audiences(
            fields=[
                CustomAudience.Field.name,
            ],
            params={'limit': 1000}
        )

        audience_list = []
        for i in range(0, len(custom_audiences)):
            audience = custom_audiences[i]
            is_checked = 0
            if('custom_audiences' in adset['targeting']):
                for default_audience in adset['targeting']['custom_audiences']:
                    if (audience['id'] == default_audience['id']):
                        is_checked = 1
                        break
            audiences = {
                'name': audience['name'],
                'id': audience['id'],
                'is_checked': is_checked,
            }
            audience_list.append(audiences)

        excluded_list = []
        for i in range(0, len(custom_audiences)):
            audience = custom_audiences[i]
            is_checked = 0
            if('excluded_custom_audiences' in adset['targeting']):
                excluded = adset['targeting']['excluded_custom_audiences']
                for default_excluded in excluded:
                    if (audience['id'] == default_excluded['id']):
                        is_checked = 1
                        break
            excludeds = {
                'name': audience['name'],
                'id': audience['id'],
                'is_checked': is_checked,
            }
            excluded_list.append(excludeds)

        result = {
            'account': self.param['account'],
            'adset': adset,
            'campaigns': campaigns,
            'gender': gender,
            'age_range': AGE_RANGE,
            'campaign_name': campaign_name,
            'country_list': country_list,
            'audience_list': audience_list,
            'excluded_list': excluded_list,
        }

        return result
