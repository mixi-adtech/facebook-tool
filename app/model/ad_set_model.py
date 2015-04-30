from facebookads.api import FacebookAdsApi
from facebookads.objects import (
    AdAccount,
    AdSet,
    AdCampaign,
    AdCreative,
    AdGroup,
)

import json, os, time

this_dir = os.path.dirname(__file__)
config_filename = os.path.join(this_dir, '../../config/config.json')

config_file = open(config_filename)
config = json.load(config_file)
config_file.close()

FacebookAdsApi.init(
    config['app_id'],
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
                AdSet.Field.promoted_object,
            ],
            params = {'limit':100}
        )

        ads = []
        for adset in adsets:
            if adset['campaign_status'] != AdGroup.Status.active:
                continue
            if not 'promoted_object' in adset:
                continue
            object_store_url = adset['promoted_object']['object_store_url'].replace('https://', 'http://')
            if object_store_url != self.link_url:
                continue
            creatives = adset.get_ad_creatives(params={'limit':50})
            campaign = AdCampaign(adset['campaign_group_id'])
            campaign.remote_read(fields=[AdCampaign.Field.name])
            ads.append({
                'id': adset['id'],
                'name': adset['name'],
                'campaign_name': campaign['name'],
                'creative_count': len(creatives),
            })
        return sorted(ads, key=lambda ad: ad['campaign_name'] + ad['name'])
