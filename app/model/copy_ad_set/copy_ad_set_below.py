from app.common.config import Config
from facebookads.api import FacebookAdsApi
from facebookads.specs import ObjectStorySpec, LinkData, AttachmentData
from facebookads.objects import (
    AdSet,
    AdCampaign,
    AdCreative,
    AdGroup,
)

import json, time, pprint, copy

pp = pprint.PrettyPrinter(indent=4)
config = Config().get_config()

FacebookAdsApi.init(
    config['api_app_id'],
    config['app_secret'],
    config['access_token'],
)

class CopyAdSet:
    def __init__(self, param):
        self.param = param

    def copy(self):
        link_url = config['link_url'][self.param['account']][self.param['os']].replace('https://', 'http://')
        campaign = AdCampaign(self.param['campaign_id'])
        campaign.remote_read(
            fields = [
                AdCampaign.Field.name
            ]
        )

        adset = AdSet(self.param['adset_id'])
        adset.remote_read(
            fields = [
                AdSet.Field.name,
                AdSet.Field.daily_budget,
                AdSet.Field.pacing_type,
                AdSet.Field.bid_info,
                'bid_type',
                AdSet.Field.promoted_object,
                AdSet.Field.targeting,
                AdSet.Field.is_autobid
            ]
        )
        # pp.pprint(adset)

        adgroups = adset.get_ad_groups(
            fields = [
                AdGroup.Field.name,
                AdGroup.Field.creative,
                AdGroup.Field.tracking_specs,
                AdGroup.Field.status
            ],
            params = {
                AdGroup.Field.status : ['ACTIVE']
            }
        )
        pp.pprint(adgroups)


        object_store_url = adset['promoted_object']['object_store_url'].replace('https://','http://')
        if link_url != object_store_url:
            return self.different_os_copy(campaign, adset, adgroups)
        else:
            return self.same_os_copy(campaign, adset, adgroups)

    def same_os_copy(self, campaign, adset, adgroups):
        parent_id = config['act_id'][self.param['account']]

        copy_targeting = copy.deepcopy(adset['targeting'])
        copy_targeting['age_max'] = self.param['age_max']
        copy_targeting['age_min'] = self.param['age_min']
        copy_targeting['geo_locations']['countries'] = self.param.getlist('countries')

        # Defaults to all. Do not specify 0.
        if(self.param['gender']):
            copy_targeting['genders'] = [self.param['gender']]
        else:
            copy_targeting['genders'] = [1,2]

        copy_adset = AdSet(parent_id=parent_id)
        copy_adset.update({
            AdSet.Field.name: self.param['adset_name'],
            AdSet.Field.daily_budget: adset['daily_budget'],
            AdSet.Field.promoted_object: adset['promoted_object'],
            'bid_type': adset['bid_type'],
            AdSet.Field.is_autobid : adset['is_autobid'],
            AdSet.Field.targeting: copy_targeting,
            AdSet.Field.status: self.param['status'],
            AdSet.Field.campaign_group_id: self.param['campaign_id']
        })
        if(not adset['is_autobid']):
            copy_adset.update({
                'bid_info': adset['bid_info']
            })
        copy_adset.remote_create()
        print("*** DONE: Copy AdSet ***")
        pp.pprint(copy_adset)

        adgroups = adset.get_ad_groups(
            fields = [
                AdGroup.Field.name,
                AdGroup.Field.creative,
                AdGroup.Field.tracking_specs,
                AdGroup.Field.status
            ],
            params = {
                AdGroup.Field.status : ['ACTIVE']
            }
        )

        for i in range(0,len(adgroups)):
            adgroup = adgroups[i]
            copy_adgroup = AdGroup(parent_id=parent_id)
            copy_adgroup.update({
                AdGroup.Field.name: adgroup['name'],
                AdGroup.Field.campaign_id: copy_adset['id'],
                AdGroup.Field.status: adgroup['adgroup_status'],
                AdGroup.Field.creative: {
                    AdGroup.Field.Creative.creative_id : adgroup['creative']['id']
                },
                AdGroup.Field.tracking_specs: adgroup['tracking_specs']
            })
            copy_adgroup.remote_create()
            print("*** DONE: Copy AdGroup ***")
            pp.pprint(copy_adgroup)

        result = {
            'adset' : copy_adset,
            'campaign' : campaign,
            'adgroups' : adgroups
        }

        return result

    def different_os_copy(self, campaign, adset, adgroups):
        parent_id = config['act_id'][self.param['account']]
        link_url = config['link_url'][self.param['account']][self.param['os']]

        copy_promoted_object = copy.deepcopy(adset['promoted_object'])
        copy_promoted_object['object_store_url'] = link_url

        copy_targeting = copy.deepcopy(adset['targeting'])
        copy_targeting['user_os'] = [config['user_os'][self.param['os']]]
        copy_targeting['age_max'] = self.param['age_max']
        copy_targeting['age_min'] = self.param['age_min']
        copy_targeting['geo_locations']['countries'] = self.param.getlist('countries')

        # Defaults to all. Do not specify 0.
        if(self.param['gender']):
            copy_targeting['genders'] = [self.param['gender']]
        else:
            copy_targeting['genders'] = [1,2]

        copy_adset = AdSet(parent_id=parent_id)
        copy_adset.update({
            AdSet.Field.name: self.param['adset_name'],
            AdSet.Field.daily_budget: adset['daily_budget'],
            AdSet.Field.promoted_object: copy_promoted_object,
            'bid_type': adset['bid_type'],
            AdSet.Field.is_autobid : adset['is_autobid'],
            AdSet.Field.targeting: copy_targeting,
            AdSet.Field.status: self.param['status'],
            AdSet.Field.campaign_group_id: self.param['campaign_id']
        })
        if(not adset['is_autobid']):
            copy_adset.update({
                'bid_info': adset['bid_info']
            })
        copy_adset.remote_create()
        print("*** DONE: Copy AdSet ***")
        pp.pprint(copy_adset)

        creatives = adset.get_ad_creatives(
            fields = [
                AdCreative.Field.name,
                AdCreative.Field.object_story_spec
            ],
            params = {
                'limit':50
            }
        )

        for i in range(0,len(adgroups)):
            adgroup = adgroups[i]

            creative = {}
            for j in range(0, len(creatives)):
                if (adgroup['creative']['id'] == creatives[j]['id']):
                    creative = creatives[j]
                    break

            object_story_spec = creative['object_story_spec']
            link_data = object_story_spec['link_data']
            call_to_action = link_data['call_to_action']

            copy_link_data = LinkData()
            copy_link_data[LinkData.Field.message] = link_data['message']
            copy_link_data[LinkData.Field.link] = link_url
            copy_link_data[LinkData.Field.multi_share_optimized] = link_data['multi_share_optimized']

            if('child_attachments' in link_data):
                copy_attachments = []
                for k in range(0,len(link_data['child_attachments'])):
                    attachment = link_data['child_attachments'][k]

                    copy_attachment = AttachmentData()
                    copy_attachment[AttachmentData.Field.link] = link_url
                    copy_attachment[AttachmentData.Field.image_hash] = attachment['image_hash']

                    copy_call_to_action = copy.deepcopy(attachment['call_to_action'])
                    copy_call_to_action['value']['link'] = link_url

                    copy_attachment[AttachmentData.Field.call_to_action] = copy_call_to_action
                    if('name' in attachment ):
                        copy_attachment[AttachmentData.Field.name] = attachment['name']
                    copy_attachments.append(copy_attachment)
                copy_link_data[LinkData.Field.child_attachments] = copy_attachments
            else:
                copy_call_to_action = copy.deepcopy(call_to_action)
                copy_call_to_action['value']['link'] = link_url

                copy_link_data[LinkData.Field.call_to_action] = copy_call_to_action
                copy_link_data[LinkData.Field.image_hash] = link_data['image_hash']


            copy_object_story_spec = ObjectStorySpec()
            copy_object_story_spec[ObjectStorySpec.Field.link_data] = copy_link_data
            copy_object_story_spec[ObjectStorySpec.Field.page_id] = object_story_spec['page_id']

            copy_creative = AdCreative(parent_id=parent_id)
            copy_creative[AdCreative.Field.name] = creative['name'],
            copy_creative[AdCreative.Field.object_story_spec] = copy_object_story_spec
            copy_creative.remote_create()
            print("*** DONE: Copy Creative ***")
            pp.pprint(copy_creative)

            time.sleep(3)

            copy_adgroup = AdGroup(parent_id=parent_id)
            copy_adgroup.update({
                AdGroup.Field.name: adgroup['name'],
                AdGroup.Field.campaign_id: copy_adset['id'],
                AdGroup.Field.status: adgroup['adgroup_status'],
                AdGroup.Field.creative: {
                    AdGroup.Field.Creative.creative_id : copy_creative['id']
                },
                AdGroup.Field.tracking_specs: adgroup['tracking_specs']
            })
            copy_adgroup.remote_create()
            print("*** DONE: Copy AdGroup ***")
            pp.pprint(copy_adgroup)
            time.sleep(3)

        result = {
            'adset' : copy_adset,
            'campaign' : campaign,
            'adgroups' : adgroups
        }

        return result
