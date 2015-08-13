from app.common.config import Config
from facebookads.api import FacebookAdsApi
from facebookads.specs import (
    AttachmentData,
    LinkData,
    ObjectStorySpec,
    VideoData
)
from facebookads.objects import (
    AdAccount,
    AdCampaign,
    AdCreative,
    AdGroup,
    AdSet,
    CustomAudience
)

import pprint
import copy

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
        store_url = config['link_url'][self.param['account']][self.param['os']]
        link_url = store_url.replace('https://', 'http://')
        campaign = AdCampaign(self.param['campaign_id'])
        campaign.remote_read(
            fields=[
                AdCampaign.Field.name
            ]
        )

        adset = AdSet(self.param['adset_id'])
        adset.remote_read(
            fields=[
                AdSet.Field.name,
                AdSet.Field.daily_budget,
                AdSet.Field.pacing_type,
                AdSet.Field.promoted_object,
                AdSet.Field.targeting,
                AdSet.Field.is_autobid,
                AdSet.Field.billing_event,
                AdSet.Field.optimization_goal,
                AdSet.Field.bid_amount,
                AdSet.Field.rtb_flag
            ]
        )
        # pp.pprint(adset)

        adgroups = adset.get_ad_groups(
            fields=[
                AdGroup.Field.name,
                AdGroup.Field.creative,
                AdGroup.Field.tracking_specs,
                AdGroup.Field.status
            ],
            params={
                AdGroup.Field.status: ['ACTIVE']
            }
        )
        # pp.pprint(adgroups)

        object_store_url = adset['promoted_object']['object_store_url']
        replace_url = object_store_url.replace('https://', 'http://')
        if link_url != replace_url:
            return self.different_os_copy(campaign, adset, adgroups)
        else:
            return self.same_os_copy(campaign, adset, adgroups)

    def same_os_copy(self, campaign, adset, adgroups):
        parent_id = config['act_id'][self.param['account']]
        account = AdAccount(parent_id)
        custom_audiences = account.get_custom_audiences(
            fields=[
                CustomAudience.Field.name,
            ],
            params={'limit': 100}
        )

        copy_custom_audience = []
        copy_excluded_custom_audience = []
        excluded_ids = self.param.getlist('excluded_custom_audiences')
        for i in range(0, len(custom_audiences)):
            custom_audience = custom_audiences[i]
            if custom_audience['id'] in self.param.getlist('custom_audiences'):
                audience = {
                    'id': custom_audience['id'],
                    'name': custom_audience['name']
                }
                copy_custom_audience.append(audience)
            if custom_audience['id'] in excluded_ids:
                excluded_audience = {
                    'id': custom_audience['id'],
                    'name': custom_audience['name']
                }
                copy_excluded_custom_audience.append(excluded_audience)

        copy_targeting = copy.deepcopy(adset['targeting'])
        copy_targeting['age_max'] = self.param['age_max']
        copy_targeting['age_min'] = self.param['age_min']
        copy_targeting['geo_locations']['countries'] = self.param.getlist('countries')
        copy_targeting['custom_audiences'] = copy_custom_audience
        copy_targeting['excluded_custom_audiences'] = copy_excluded_custom_audience

        # Defaults to all. Do not specify 0.
        if(self.param['gender']):
            copy_targeting['genders'] = [self.param['gender']]
        else:
            copy_targeting['genders'] = [1, 2]

        copy_adset = AdSet(parent_id=parent_id)
        copy_adset.update({
            AdSet.Field.name: self.param['adset_name'],
            AdSet.Field.daily_budget: adset['daily_budget'],
            AdSet.Field.promoted_object: adset['promoted_object'],
            AdSet.Field.is_autobid: adset['is_autobid'],
            AdSet.Field.targeting: copy_targeting,
            AdSet.Field.status: self.param['status'],
            AdSet.Field.campaign_group_id: self.param['campaign_id'],
            AdSet.Field.billing_event: adset['billing_event'],
            AdSet.Field.optimization_goal: adset['optimization_goal'],
            AdSet.Field.rtb_flag: adset['rtb_flag']
        })

        if 'bid_amount' in adset:
            copy_adset.update({
                AdSet.Field.bid_amount: adset['bid_amount']
            })

        copy_adset.remote_create()
        print("*** DONE: Copy AdSet ***")
        pp.pprint(copy_adset)

        adgroups = adset.get_ad_groups(
            fields=[
                AdGroup.Field.name,
                AdGroup.Field.creative,
                AdGroup.Field.tracking_specs,
                AdGroup.Field.status
            ],
            params={
                AdGroup.Field.status: ['ACTIVE']
            }
        )

        for i in range(0, len(adgroups)):
            adgroup = adgroups[i]
            copy_adgroup = AdGroup(parent_id=parent_id)
            copy_adgroup.update({
                AdGroup.Field.name: adgroup['name'],
                AdGroup.Field.campaign_id: copy_adset['id'],
                AdGroup.Field.status: adgroup['adgroup_status'],
                AdGroup.Field.creative: {
                    AdGroup.Field.Creative.creative_id: adgroup['creative']['id']
                },
                AdGroup.Field.tracking_specs: adgroup['tracking_specs']
            })
            copy_adgroup.remote_create()
            print("*** DONE: Copy AdGroup ***")
            pp.pprint(copy_adgroup)

        result = {
            'adset': copy_adset,
            'campaign': campaign,
            'adgroups': adgroups
        }

        return result

    def different_os_copy(self, campaign, adset, adgroups):
        parent_id = config['act_id'][self.param['account']]
        link_url = config['link_url'][self.param['account']][self.param['os']]

        account = AdAccount(parent_id)
        custom_audiences = account.get_custom_audiences(
            fields=[
                CustomAudience.Field.name,
            ],
            params={'limit': 100}
        )

        copy_custom_audience = []
        copy_excluded_audience = []
        for i in range(0, len(custom_audiences)):
            custom_audience = custom_audiences[i]
            if custom_audience['id'] in self.param.getlist('custom_audiences'):
                audience = {
                    'id': custom_audience['id'],
                    'name': custom_audience['name']
                }
                copy_custom_audience.append(audience)
            if custom_audience['id'] in self.param.getlist('excluded_custom_audiences'):
                excluded_audience = {
                    'id': custom_audience['id'],
                    'name': custom_audience['name']
                }
                copy_excluded_audience.append(excluded_audience)

        copy_promoted_object = copy.deepcopy(adset['promoted_object'])
        copy_promoted_object['object_store_url'] = link_url

        copy_targeting = copy.deepcopy(adset['targeting'])
        copy_targeting['user_os'] = [config['user_os'][self.param['os']]]
        copy_targeting['age_max'] = self.param['age_max']
        copy_targeting['age_min'] = self.param['age_min']
        copy_targeting['geo_locations']['countries'] = self.param.getlist('countries')
        copy_targeting['custom_audiences'] = copy_custom_audience
        copy_targeting['excluded_custom_audiences'] = copy_excluded_audience

        # Default to all.
        if 'user_device' in copy_targeting:
            del copy_targeting['user_device']

        # Defaults to all. Do not specify 0.
        if(self.param['gender']):
            copy_targeting['genders'] = [self.param['gender']]
        else:
            copy_targeting['genders'] = [1, 2]

        copy_adset = AdSet(parent_id=parent_id)
        copy_adset.update({
            AdSet.Field.name: self.param['adset_name'],
            AdSet.Field.daily_budget: adset['daily_budget'],
            AdSet.Field.promoted_object: copy_promoted_object,
            AdSet.Field.is_autobid: adset['is_autobid'],
            AdSet.Field.targeting: copy_targeting,
            AdSet.Field.status: self.param['status'],
            AdSet.Field.campaign_group_id: self.param['campaign_id'],
            AdSet.Field.billing_event: adset['billing_event'],
            AdSet.Field.optimization_goal: adset['optimization_goal'],
            AdSet.Field.rtb_flag: adset['rtb_flag']
        })

        if 'bid_amount' in adset:
            copy_adset.update({
                AdSet.Field.bid_amount: adset['bid_amount']
            })
        copy_adset.remote_create()
        print("*** DONE: Copy AdSet ***")
        pp.pprint(copy_adset)

        creatives = adset.get_ad_creatives(
            fields=[
                AdCreative.Field.name,
                AdCreative.Field.object_story_spec
            ],
            params={
                'limit': 50
            }
        )

        for i in range(0, len(adgroups)):
            adgroup = adgroups[i]

            creative = {}
            for j in range(0, len(creatives)):
                if (adgroup['creative']['id'] == creatives[j]['id']):
                    creative = creatives[j]
                    break

            object_story_spec = creative['object_story_spec']
            if 'link_data' in object_story_spec:
                copy_object_story_spec = self.get_object_story_spec_for_image(
                    object_story_spec,
                    link_url
                )
            elif 'video_data' in object_story_spec:
                copy_object_story_spec = self.get_object_story_spec_for_video(
                    object_story_spec,
                    link_url
                )
            else:
                break

            copy_creative = AdCreative(parent_id=parent_id)
            copy_creative[AdCreative.Field.name] = creative['name'],
            copy_creative[AdCreative.Field.object_story_spec] = copy_object_story_spec
            copy_creative.remote_create()
            print("*** DONE: Copy Creative ***")
            pp.pprint(copy_creative)

            copy_adgroup = AdGroup(parent_id=parent_id)
            copy_adgroup.update({
                AdGroup.Field.name: adgroup['name'],
                AdGroup.Field.campaign_id: copy_adset['id'],
                AdGroup.Field.status: adgroup['adgroup_status'],
                AdGroup.Field.creative: {
                    AdGroup.Field.Creative.creative_id: copy_creative['id']
                },
                AdGroup.Field.tracking_specs: adgroup['tracking_specs']
            })
            copy_adgroup.remote_create()
            print("*** DONE: Copy AdGroup ***")
            pp.pprint(copy_adgroup)

        result = {
            'adset': copy_adset,
            'campaign': campaign,
            'adgroups': adgroups
        }

        return result

    def get_object_story_spec_for_image(self, object_story_spec, link_url):
        link_data = object_story_spec['link_data']
        call_to_action = link_data['call_to_action']
        copy_link_data = LinkData()
        copy_link_data[LinkData.Field.message] = link_data['message']
        copy_link_data[LinkData.Field.link] = link_url
        copy_link_data[LinkData.Field.multi_share_optimized] = link_data['multi_share_optimized']

        if('child_attachments' in link_data):
            copy_attachments = []
            for k in range(0, len(link_data['child_attachments'])):
                attachment = link_data['child_attachments'][k]

                copy_attachment = AttachmentData()
                copy_attachment[AttachmentData.Field.link] = link_url
                copy_attachment[AttachmentData.Field.image_hash] = attachment['image_hash']

                copy_call_to_action = copy.deepcopy(attachment['call_to_action'])
                copy_call_to_action['value']['link'] = link_url

                copy_attachment[AttachmentData.Field.call_to_action] = copy_call_to_action
                if 'name' in attachment:
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

        return copy_object_story_spec

    def get_object_story_spec_for_video(self, object_story_spec, link_url):
        video_data = object_story_spec['video_data']
        call_to_action = video_data['call_to_action']
        copy_call_to_action = copy.deepcopy(call_to_action)
        copy_call_to_action['value']['link'] = link_url

        copy_video_data = VideoData()
        copy_video_data[VideoData.Field.description] = video_data['description']
        copy_video_data[VideoData.Field.image_url] = video_data['image_url']
        copy_video_data[VideoData.Field.video_id] = video_data['video_id']
        if 'title' in video_data:
            copy_video_data[VideoData.Field.title] = video_data['title']

        copy_video_data[VideoData.Field.call_to_action] = copy_call_to_action

        copy_object_story_spec = ObjectStorySpec()
        copy_object_story_spec[ObjectStorySpec.Field.video_data] = copy_video_data
        copy_object_story_spec[ObjectStorySpec.Field.page_id] = object_story_spec['page_id']

        return copy_object_story_spec
