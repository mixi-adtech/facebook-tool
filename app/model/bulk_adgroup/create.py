from app.common.config import Config
from facebookads import FacebookAdsApi
from facebookads.specs import ObjectStorySpec, LinkData
from facebookads.objects import (
    AdImage,
    AdCreative,
    AdGroup,
)

import os
import pprint

pp = pprint.PrettyPrinter(indent=4)
this_dir = os.path.dirname(__file__)
config = Config().get_config()

FacebookAdsApi.init(
    config['api_app_id'],
    config['app_secret'],
    config['access_token'],
)


class AdCreativeModel:
    def __init__(self, param, filename):
        self.param = param
        self.filename = filename

    def create_ad_creative(self):
        parent_id = config['act_id'][self.param['account']]
        page_id = config['page_id'][self.param['account']]
        link_url = config['link_url'][self.param['account']][self.param['os']]

        # Upload an image to an account.
        img = AdImage(parent_id=parent_id)
        img[AdImage.Field.filename] = os.path.join(
            this_dir,
            '../../../upload/' + self.filename
        )
        img.remote_create()
        print("**** DONE: Image uploaded:")
        pp.pprint(img)
        # The image hash can be found using img[AdImage.Field.hash]

        # Create link data
        link_data = LinkData()
        link_data[LinkData.Field.link] = link_url
        link_data[LinkData.Field.message] = self.param['message']
        link_data[LinkData.Field.image_hash] = img.get_hash()
        call_to_action = {'type': 'INSTALL_MOBILE_APP'}
        call_to_action['value'] = {
            'link': link_url,
            'link_title': self.param['title'],
            'application': config['app_id'][self.param['account']],
        }
        link_data[LinkData.Field.call_to_action] = call_to_action

        # Create object story spec
        object_story_spec = ObjectStorySpec()
        object_story_spec[ObjectStorySpec.Field.page_id] = page_id
        object_story_spec[ObjectStorySpec.Field.link_data] = link_data

        # Create a creative
        creative = AdCreative(parent_id=parent_id)
        creative[AdCreative.Field.name] = self.param['creative_name']
        creative[AdCreative.Field.object_story_spec] = object_story_spec
        creative.remote_create()

        print("**** DONE: Creative created:")
        pp.pprint(creative)

        # Get excited, we are finally creating an ad!!!
        adset_ids = self.param.getlist('adset_ids')
        ads = []
        for adset_id in adset_ids:
            ad = AdGroup(parent_id=parent_id)
            ad.update({
                AdGroup.Field.name: self.param['creative_name'],
                AdGroup.Field.campaign_id: adset_id,
                AdGroup.Field.status: self.param['status'],
                AdGroup.Field.creative: {
                    AdGroup.Field.Creative.creative_id: creative['id'],
                },
                AdGroup.Field.tracking_specs: [
                    {
                        'action.type': ['mobile_app_install'],
                        'application': config['app_id'][self.param['account']],
                    },
                ],
            })
            ad.remote_create()
            ads.append(ad)
        print("**** DONE: Ad created:")
        pp.pprint(ads)
        return ads
