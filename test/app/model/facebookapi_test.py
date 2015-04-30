import unittest
from mock import MagicMock, patch

import sys, os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path + '/../../../')
from app.model.facebookapi import GetFacebookAdset

class MockAdSet:
    def __init__(self, id, name, campaign_group_id, campaign_status):
        self.id = id
        self.name = name
        self.campaign_group_id = campaign_group_id
        self.campaign_status   = campaign_status
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def get_ad_creatives(self, fields):
        return [0] * fields[0]()

class FacebookAdsApiTest(unittest.TestCase):
    def test_getAdSet(self):
        expectAds = [
            {
                'id'             : 1234,
                'name'           : 'hoge',
                'campaign_name'  : 'campaign_name',
                'creative_count' : 3,
            },
            {
                'id'             : 9999,
                'name'           : 'moga',
                'campaign_name'  : 'campaign_name',
                'creative_count' : 3,
            },
        ]
        mockAds1 = MockAdSet(1234, 'hoge', 5, 'ACTIVE')
        mockAds2 = MockAdSet(5555, 'fuga', 12, 'CAMPAIGN_GROUP_PAUSED')
        mockAds3 = MockAdSet(9999, 'moga', 33, 'ACTIVE')
        account = MagicMock()
        account.get_ad_sets.return_value = [mockAds1, mockAds2, mockAds3]

        with patch('app.model.facebookapi.AdAccount', return_value=account) as _mock_account:
            with patch('app.model.facebookapi.AdCreative.Field.object_story_id', return_value=3) as _mock_creative:

                campaign_name = { 'name' : 'campaign_name' }
                def getitem(name):
                    return campaign_name[name]

                campaign = MagicMock(side_effect=getitem)
                campaign.__getitem__.side_effect = getitem
                campaign.remote_read.return_value = {}

                with patch('app.model.facebookapi.AdCampaign', return_value=campaign) as _mock_campaign:
                    model = GetFacebookAdset('us')
                    ads   = model.getAdSet()

                    self.assertEqual(ads, expectAds)


if __name__ == '__main__':
    unittest.main()
