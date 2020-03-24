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
        url_run_list = reverse.reverse('executors:runs-list')
        response = self.client.post(url_run_list, data={
            'procedure': 'test-procedure-1',
        })
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url_run_list, data={
            'procedure': 'test-procedure-1',
            'inputs': [3.0, 4.0],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(response.data.get('outputs'), [19.0, 84.0])
        run_uuid = response.data.get('uuid')
        self.assertIsNotNone(run_uuid)

        # check result again
        url_run_detail = reverse.reverse(
            'executors:runs-detail', [run_uuid])
        response = self.client.get(url_run_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'finished')
        self.assertListEqual(response.data.get('outputs'), [19.0, 84.0])

    @skip('async run is not ready')
    def test_create_procedure_run_async(self):
        url_run_async = reverse.reverse('executors:runs-async')
        response = self.client.post(url_run_async, data={
            'procedure': 'test-procedure-1',
            'inputs': [3.0, 4.0],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('outputs'))
