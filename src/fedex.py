import time
import requests
import logging

# TODO: correlate all statuses
fedex_codes_to_zankraft = {
    ('OC', 'PM'): 'CREATED',
    ('DL', 'PU'): 'DELIVERED',
    ('DP', 'IT'): 'IN_TRANSIT',
    ('DE', ): 'EXCEPTION',
    ('HL', ): 'OUT_FOR_DELIVERY',
}

class RequestException(Exception):
    pass


class FedEx:
    client_id = 'l7ecac81c1e42b46ec9eab51a7d8134e09'
    client_secret = 'baf2dbabe32a4a9aa8fb3eac42555329'
    url = 'https://apis-sandbox.fedex.com/'
    loger = logging.getLogger('Fedex')


    # TODO: cache token to avoid each time request
    def auth(self):
        url = self.url + "oauth/token"

        payload = {'grant_type': 'client_credentials',
                   'client_id': self.client_id,
                   'client_secret': self.client_secret}

        headers = {
            'Content-Type': "application/x-www-form-urlencoded"
        }

        response = self.post(url, data=payload, headers=headers)
        if not response:
            raise RequestException('Auth request error')

        resp_dict = response.json()
        self.barear = resp_dict['access_token']


    def track(self, track_number):
        url = self.url + "track/v1/trackingnumbers"

        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [{
                "trackingNumberInfo": {
                    "trackingNumber": track_number
                }
            }]
        }

        headers = {
            'Content-Type': "application/json",
            'Authorization': f"Bearer {self.barear}"
        }

        response = self.post(url, json=payload, headers=headers)
        if not response:
            raise RequestException('Track request error')

        return self._build_zenkraft_result(response)


    def _build_zenkraft_result(self, response):
        resp_dict = response.json()
        complete_track_results = resp_dict['output']['completeTrackResults']
        if not complete_track_results:
            self.loger.warning(f'results are empty')
            return {}
        track_results = complete_track_results[0]['trackResults']
        if not track_results:
            self.loger.warning(f'track results are empty')
            return {}

        # TODO: check if it is possible to have couple of track results and what does it mean.
        track = track_results[0]

        # print(resp_dict)
        result = {
            "carrier": "fedex",
            "delivered": False,
            "tracking_number": complete_track_results[0]['trackingNumber'],
            "status": track['latestStatusDetail']['description'],
            "checkpoints": []
        }

        status_code = track['latestStatusDetail']['code']
        if status_code == 'DL':
            result['delivered'] = True

        for codes, stage in fedex_codes_to_zankraft.items():
            if status_code in codes:
                result['tracking_stage'] = stage

        for date_time in track['dateAndTimes']:
            if date_time['type'] == 'ACTUAL_DELIVERY':
                result['delivery_date'] = date_time['dateTime']
            if date_time['type'] == 'ESTIMATED_DELIVERY':
                result['estimated_delivery'] = date_time['dateTime']

        #checkpoints
        for event in track['scanEvents']:
            checkpoint = {
                'description': event['eventDescription'],
                'status': event['eventDescription'],
                'time': event['date'],
            }
            for codes, stage in fedex_codes_to_zankraft.items():
                if event['derivedStatusCode'] in codes:
                    checkpoint['tracking_stage'] = stage
            result['checkpoints'].append(checkpoint)

        return result


    def post(self, url, **kwargs):
        for _ in range(0, 10):  # 10 attempts
            response = requests.post(url, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(3)
            print(f'trying to rich {url}. status: {response.status_code}')

        self.loger.error(f'Request error with status: {response.status_code}\n'
                         f'url: {url}\n'
                         f'response: {response.content}')
