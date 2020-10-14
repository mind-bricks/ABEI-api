from unittest import skip

from rest_framework import (
    reverse,
    status,
    test,
)


class ProcedureRunTest(test.APITestCase):
    fixtures = [
        'test_executors.json',
    ]

    def test_create_procedure_run(self):
        url_run_list = reverse.reverse('executors:runs-list', [
            'test-site-1',
            'test-procedure-1',
        ])
        response = self.client.post(url_run_list, data={})
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url_run_list, data={
            'inputs': [3.0, 4.0],
        })
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(response.data.get('outputs'), [19.0, 84.0])
        run_uuid = response.data.get('uuid')
        self.assertIsNotNone(run_uuid)

        # check result again
        url_run_detail = reverse.reverse('executors:runs-detail', [
            'test-site-1',
            'test-procedure-1',
            run_uuid,
        ])
        response = self.client.get(url_run_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'finished')
        self.assertListEqual(response.data.get('outputs'), [19.0, 84.0])

        # check logs
        url_run_log = reverse.reverse('executors:run-logs-list')
        response = self.client.get(url_run_log)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data.get('count'), 0)

    @skip('async run is not ready')
    def test_create_procedure_run_async(self):
        url_run_async = reverse.reverse('executors:runs-async', [
            'test-site-1',
            'test-procedure-1',
        ])
        response = self.client.post(url_run_async, data={
            'inputs': [3.0, 4.0],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('outputs'))
