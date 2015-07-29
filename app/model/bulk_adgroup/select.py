from app.common.config import Config
from facebookads.api import FacebookAdsApi
from facebookads.objects import (
    AdAccount,
    AdSet,
    AdCampaign,
    AdCreative,
    AdGroup,
)

import json, os, pprint

pp = pprint.PrettyPrinter(indent=4)
config = Config().get_config()

FacebookAdsApi.init(
    config['api_app_id'],
    config['app_secret'],
    config['access_token'],
)

class AdSetModel:
    def __init__(self, act_id, link_url):
        self.act_id = act_id
        self.link_url = link_url.replace('https://', 'http://')

    def get_ad_set(self):
        account = AdAccount(self.act_id)
        adsets = account.get_ad_sets(
            fields=[
                AdSet.Field.name,
                AdSet.Field.status,
                AdSet.Field.campaign_group_id,
                AdSet.Field.promoted_object
            ],
            params = {
                'campaign_status' : ['ACTIVE'],
                'limit':100
            }
        )

        campaigns = account.get_ad_campaigns(
            fields=[
                AdCampaign.Field.name,
                AdCampaign.Field.status,
                AdCampaign.Field.objective
            ],
            params={
                'campaign_group_status':['ACTIVE']
            }
        );

        ads = []
        for adset in adsets:
            if not 'promoted_object' in adset:
                continue
            object_store_url = adset['promoted_object']['object_store_url'].replace('https://', 'http://')
            if object_store_url != self.link_url:
                continue
            creatives = adset.get_ad_creatives(params={'limit':50})
            for i in range(0,len(campaigns)):
                campaign = campaigns[i]
                if adset['campaign_group_id'] == campaign['id']:
                    ads.append({
                        'id': adset['id'],
                        'name': adset['name'],
                        'campaign_name': campaign['name'],
                        'campaign_objective' : campaign['objective'],
                        'creative_count': len(creatives),
                    })
                    break
        return sorted(ads, key=lambda ad: ad['campaign_name'] + ad['name'])
